"""Create a backup file."""

import errno
import os
import shutil
import sys
import tempfile
import zipfile
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import BinaryIO
lazy import platform  # only needed when writing the manifest

from obs_backup import __version__
from obs_backup.backup.collect import collect_files, scan_media
from obs_backup.backup.errors import BackupError
from obs_backup.backup.layout import CONFIG_PREFIX, MANIFEST, MEDIA_PREFIX
from obs_backup.backup.manifest import Manifest
from obs_backup.backup.models import BackupResult, MediaRef, Progress, Selection
from obs_backup.obs import config as obs_config
from obs_backup.obs.media import file_name

# Already-compressed formats are stored as they are; deflating them only costs time.
STORED_SUFFIXES = frozenset({
    ".mp4", ".mkv", ".mov", ".webm", ".flv", ".avi", ".mp3", ".ogg", ".m4a", ".aac",
    ".opus", ".flac", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".7z",
})  # fmt: skip

# Config files up to this size are read into memory before they are added to the
# backup; larger ones (plugins, browser data) go through a temporary file.
SPOOL_IN_MEMORY = 32 << 20
CHUNK = 1 << 20


def default_backup_name(suffix: str = "") -> str:
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"obs-backup_{stamp}{suffix}.zip"


def new_backup_path(folder: Path, suffix: str = "") -> Path:
    """A path in ``folder`` for a new backup that no other backup uses yet.

    Backups are named after the current second; a second backup in the same
    second gets a number: ``obs-backup_<time>_2.zip``.
    """
    name = Path(default_backup_name(suffix))
    path, n = folder / name, 2
    while path.exists() or _part(path).exists():
        path = folder / f"{name.stem}_{n}{name.suffix}"
        n += 1
    return path


def _part(dest: Path) -> Path:
    return dest.with_name(dest.name + ".part")


def _compression(path: str) -> int:
    if Path(path).suffix.lower() in STORED_SUFFIXES:
        return zipfile.ZIP_STORED
    return zipfile.ZIP_DEFLATED


class _Unreadable(Exception):
    """A file to back up could not be read; the backup goes on without it.

    Kept apart from errors writing the backup itself (a full disk, a network
    folder that went away), which end the backup.
    """


def _member_info(
    zf: zipfile.ZipFile, path: Path, arcname: str, compression: int
) -> zipfile.ZipInfo:
    try:
        info = zipfile.ZipInfo.from_file(path, arcname, strict_timestamps=False)
    except OSError as e:
        raise _Unreadable from e
    info.compress_type = compression
    info.compress_level = zf.compresslevel
    return info


def _open_source(path: Path) -> BinaryIO:
    try:
        return path.open("rb")
    except OSError as e:
        raise _Unreadable from e


def _chunks(src: BinaryIO) -> Iterator[bytes]:
    while True:
        try:
            chunk = src.read(CHUNK)
        except OSError as e:
            raise _Unreadable from e
        if not chunk:
            return
        yield chunk


def _add_complete_file(zf: zipfile.ZipFile, path: Path, arcname: str) -> int:
    """Add the file at ``path`` as ``arcname`` and return its size.

    The file is read completely before the member is started: copying it straight
    in would leave a truncated member behind if reading failed halfway (a file OBS
    holds locked), and a restore would then write that truncated file.
    """
    info = _member_info(zf, path, arcname, zf.compression)
    with tempfile.SpooledTemporaryFile(max_size=SPOOL_IN_MEMORY) as copy:
        with _open_source(path) as src:
            for chunk in _chunks(src):
                copy.write(chunk)
        copy.seek(0)
        with zf.open(info, "w") as dst:
            shutil.copyfileobj(copy, dst, CHUNK)
    return info.file_size  # what was written, set when the member was closed


def _add_media_file(zf: zipfile.ZipFile, path: str, arcname: str) -> int:
    """Add the media file at ``path`` as ``arcname`` and return its size.

    Media can be large, so it is not copied first. A file that fails halfway
    leaves an unused member: the manifest lists only media written completely.
    """
    info = _member_info(zf, Path(path), arcname, _compression(path))
    with _open_source(Path(path)) as src, zf.open(info, "w") as dst:
        for chunk in _chunks(src):
            dst.write(chunk)
    return info.file_size


def _publish(tmp: Path, dest: Path) -> None:
    """Rename the finished ``tmp`` to ``dest``, never replacing a file there.

    Another backup can take the name while this one is written (a second copy of
    the app); renaming then raises ``FileExistsError``.
    """
    if sys.platform == "win32":
        os.rename(tmp, dest)  # refuses to replace an existing file
        return
    try:
        os.link(tmp, dest)  # refuses as well; os.rename would replace
    except FileExistsError:
        raise
    except OSError:  # no hard links on this drive (FAT, some network folders)
        if dest.exists():
            raise FileExistsError(errno.EEXIST, "file exists", str(dest)) from None
        os.replace(tmp, dest)
        return
    tmp.unlink()


def create_backup(
    config_dir: Path, dest: Path, sel: Selection, progress: Progress | None = None
) -> BackupResult:
    """Write the selected parts of ``config_dir`` (and optionally media) to ``dest``.

    The zip is written to ``dest.part`` first and renamed when complete, so an
    interrupted backup never leaves a broken file under the final name. An
    existing file at ``dest`` is never replaced (see ``new_backup_path``).
    Files that can't be read (usually because OBS has them open) are skipped,
    listed in the result and recorded in the manifest. An error writing ``dest``
    ends the backup.
    """
    config_dir = Path(config_dir)
    if not config_dir.is_dir():
        raise BackupError("config_dir_not_found", dir=config_dir)
    if sel.is_empty():
        raise BackupError("nothing_selected")
    if dest.exists():
        raise BackupError("backup_exists", path=dest)

    unreadable: list[Path] = []
    files = collect_files(config_dir, sel, unreadable)
    media = scan_media(config_dir, sel.scene_collections) if sel.media else []
    total = len(files) + len(media)
    result = BackupResult(path=dest, files=0, total_bytes=0)

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = _part(dest)
    # strict_timestamps=False: files dated before 1980 (which zip can't store)
    # get 1980-01-01 instead of failing the whole backup.
    try:  # "x": another backup being written under the same name is left alone
        zf = zipfile.ZipFile(
            tmp, "x", zipfile.ZIP_DEFLATED, compresslevel=6, strict_timestamps=False
        )
    except FileExistsError as e:
        raise BackupError("backup_in_progress", path=dest) from e
    done = 0
    try:
        with zf:
            # A folder that can't be listed counts as skipped, written with a "/".
            skipped_config = [f"{d.relative_to(config_dir).as_posix()}/" for d in unreadable]
            for path in files:
                rel = path.relative_to(config_dir).as_posix()
                if progress:
                    progress(done, total, rel)
                try:
                    result.total_bytes += _add_complete_file(zf, path, CONFIG_PREFIX + rel)
                    result.files += 1
                except _Unreadable:
                    skipped_config.append(rel)
                done += 1

            written_media: list[MediaRef] = []
            skipped_media: list[str] = []
            for i, ref in enumerate(media, 1):
                ref.archive = f"{MEDIA_PREFIX}{i:04d}_{file_name(ref.original)}"
                if progress:
                    progress(done, total, ref.original)
                try:
                    ref.size = _add_media_file(zf, ref.original, ref.archive)
                    written_media.append(ref)
                    result.files += 1
                    result.total_bytes += ref.size
                except _Unreadable:
                    skipped_media.append(ref.original)
                done += 1

            manifest = _manifest(config_dir, sel, written_media, skipped_config)
            zf.writestr(MANIFEST, manifest.to_json())
        try:
            _publish(tmp, dest)
        except FileExistsError as e:
            raise BackupError("backup_exists", path=dest) from e
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    result.skipped = skipped_config + skipped_media
    if progress:
        progress(total, total, "")
    return result


def _manifest(
    config_dir: Path, sel: Selection, media: list[MediaRef], skipped: list[str]
) -> Manifest:
    profiles = [p for p in obs_config.list_profiles(config_dir) if p.dir_name in sel.profiles]
    scenes = [
        s
        for s in obs_config.list_scene_collections(config_dir)
        if s.file_name in sel.scene_collections
    ]
    return Manifest(
        created=datetime.now().astimezone().isoformat(timespec="seconds"),
        app_version=__version__,
        source_os=platform.system(),
        obs_version=obs_config.obs_version(config_dir),
        config_dir=str(config_dir),
        profiles=[{"name": p.name, "dir": p.dir_name} for p in profiles],
        scene_collections=[{"name": s.name, "file": s.file_name} for s in scenes],
        global_settings=sel.global_settings,
        plugin_config=sel.plugin_config,
        browser_data=sel.browser_data,
        plugins=sel.plugins,
        media=media,
        skipped=skipped,
    )
