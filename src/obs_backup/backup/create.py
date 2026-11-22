"""Create a backup file."""

from __future__ import annotations

import os
import platform
import zipfile
from datetime import datetime
from pathlib import Path

from obs_backup import __version__
from obs_backup.backup.collect import collect_files, scan_media
from obs_backup.backup.errors import BackupError
from obs_backup.backup.layout import CONFIG_PREFIX, MANIFEST, MEDIA_PREFIX
from obs_backup.backup.manifest import Manifest
from obs_backup.backup.models import BackupResult, MediaRef, Progress, Selection
from obs_backup.obs import config as obs_config
from obs_backup.obs.media import file_name

# Already-compressed formats are stored as they are; deflating them only costs time.
STORED_SUFFIXES = {
    ".mp4", ".mkv", ".mov", ".webm", ".flv", ".avi", ".mp3", ".ogg", ".m4a", ".aac",
    ".opus", ".flac", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".7z",
}  # fmt: skip


def default_backup_name(suffix: str = "") -> str:
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"obs-backup_{stamp}{suffix}.zip"


def _compression(path: str) -> int:
    if Path(path).suffix.lower() in STORED_SUFFIXES:
        return zipfile.ZIP_STORED
    return zipfile.ZIP_DEFLATED


def create_backup(
    config_dir: Path, dest: Path, sel: Selection, progress: Progress | None = None
) -> BackupResult:
    """Write the selected parts of ``config_dir`` (and optionally media) to ``dest``.

    The zip is written to ``dest.part`` first and renamed when complete, so an
    interrupted backup never leaves a broken file under the final name.
    Files that can't be read (usually because OBS has them open) are skipped
    and listed in the result.
    """
    config_dir = Path(config_dir)
    if not config_dir.is_dir():
        raise BackupError(f"OBS config folder not found: {config_dir}")
    if sel.is_empty():
        raise BackupError("nothing selected")

    files = collect_files(config_dir, sel)
    media = scan_media(config_dir, sel.scene_collections) if sel.media else []
    total = len(files) + len(media)
    result = BackupResult(path=dest, files=0, total_bytes=0)

    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + ".part")
    done = 0
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for path in files:
                rel = path.relative_to(config_dir).as_posix()
                if progress:
                    progress(done, total, rel)
                try:
                    zf.write(path, CONFIG_PREFIX + rel)
                    result.files += 1
                    result.total_bytes += path.stat().st_size
                except OSError:
                    result.skipped.append(rel)
                done += 1

            written_media: list[MediaRef] = []
            for i, ref in enumerate(media, 1):
                ref.archive = f"{MEDIA_PREFIX}{i:04d}_{file_name(ref.original)}"
                if progress:
                    progress(done, total, ref.original)
                try:
                    zf.write(ref.original, ref.archive, compress_type=_compression(ref.original))
                    written_media.append(ref)
                    result.files += 1
                    result.total_bytes += ref.size
                except OSError:
                    result.skipped.append(ref.original)
                done += 1

            zf.writestr(MANIFEST, _manifest(config_dir, sel, written_media).to_json())
        os.replace(tmp, dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    if progress:
        progress(total, total, "")
    return result


def _manifest(config_dir: Path, sel: Selection, media: list[MediaRef]) -> Manifest:
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
    )
