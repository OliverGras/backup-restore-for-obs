"""Restore a backup file into an OBS config folder."""

import json
import os
import shutil
import tempfile
import zipfile
import zlib
from pathlib import Path

from obs_backup.backup.collect import safety_selection
from obs_backup.backup.create import create_backup, default_backup_name
from obs_backup.backup.errors import ZIP_ERRORS, InvalidBackupError, RestoreFailedError
from obs_backup.backup.layout import CONFIG_PREFIX, is_plain_name
from obs_backup.backup.manifest import Manifest, read_manifest
from obs_backup.backup.models import MediaRef, Progress, RestoreResult, Selection
from obs_backup.obs import config as obs_config
from obs_backup.obs.media import dump_scene_json, file_name, rewrite_paths

_PROFILES = obs_config.PROFILES_DIR.as_posix()
_SCENES = obs_config.SCENES_DIR.as_posix()
_BROWSER = obs_config.BROWSER_DIR.as_posix()
_PLUGIN_CONFIG = obs_config.PLUGIN_CONFIG_DIR.as_posix()
_PLUGINS = obs_config.PLUGINS_DIR.as_posix()


def _is_selected(rel: str, sel: Selection) -> bool:
    """Whether a file at ``rel`` (relative to the config folder) belongs to ``sel``."""
    parts = rel.split("/")
    if rel.startswith(f"{_PROFILES}/") and len(parts) > 3:
        return parts[2] in sel.profiles
    if rel.startswith(f"{_SCENES}/") and len(parts) == 3:
        return parts[2] in sel.scene_collections
    if rel in obs_config.GLOBAL_FILES or parts[0] in obs_config.GLOBAL_DIRS:
        return sel.global_settings
    if rel.startswith(f"{_BROWSER}/"):
        return sel.browser_data
    if rel.startswith(f"{_PLUGIN_CONFIG}/"):
        return sel.plugin_config
    if parts[0] == _PLUGINS:
        return sel.plugins
    return False


def members_for(names: list[str], sel: Selection) -> list[str]:
    """Zip members under ``config/`` that ``sel`` covers."""
    return [
        n
        for n in names
        if n.startswith(CONFIG_PREFIX)
        and not n.endswith("/")
        and _is_selected(n[len(CONFIG_PREFIX) :], sel)
    ]


def safe_target(base: Path, rel: str) -> Path:
    """``base / rel``, refusing paths that are not inside ``base`` (zip slip).

    ``..``, ``.`` and empty segments are refused even when the path stays inside
    ``base``: ``basic/profiles/P/../../../plugins/x`` would otherwise pass as a
    file of profile ``P`` and land in a part of the folder that was not selected.
    (``zipfile`` turns backslashes in member names into ``/`` on Windows.)
    """
    if any(part in ("", ".", "..") for part in rel.split("/")):
        raise InvalidBackupError(f"unsafe path in backup: {rel}")
    base = base.resolve()
    target = (base / rel).resolve()
    if base not in target.parents:
        raise InvalidBackupError(f"unsafe path in backup: {rel}")
    return target


def _crc32(path: Path) -> int:
    crc = 0
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            crc = zlib.crc32(chunk, crc)
    return crc


def _has_contents(path: Path, info: zipfile.ZipInfo) -> bool:
    """Whether the file at ``path`` holds exactly the zip member ``info``."""
    try:
        return path.is_file() and path.stat().st_size == info.file_size and _crc32(path) == info.CRC
    except OSError:
        return False


def unique_media_target(
    media_dir: Path, name: str, info: zipfile.ZipInfo, taken: set[Path]
) -> Path:
    """Where to put the media file ``info`` in ``media_dir``.

    A file that already holds the same contents (restored before) is reused. Any
    other existing file, and any name already given to another media file of this
    restore (``taken``), gets a numbered name instead: ``logo_2.png``.
    """
    target = media_dir / name
    stem, suffix = target.stem, target.suffix
    n = 2
    while target in taken or (target.exists() and not _has_contents(target, info)):
        target = media_dir / f"{stem}_{n}{suffix}"
        n += 1
    taken.add(target)
    return target


def _plan_media(
    manifest: Manifest,
    sel: Selection,
    media_dir: Path | None,
    infos: dict[str, zipfile.ZipInfo],
    result: RestoreResult,
) -> tuple[list[tuple[MediaRef, Path]], dict[str, str]]:
    """Media files to extract, and the path rewrites for the scene collections."""
    jobs: list[tuple[MediaRef, Path]] = []
    mapping: dict[str, str] = {}
    taken: set[Path] = set()
    for ref in manifest.media:
        if not set(ref.used_by) & set(sel.scene_collections):
            continue
        try:
            if Path(ref.original).is_file():
                continue  # still where the scene collection expects it
        except OSError, ValueError:
            pass
        name = file_name(ref.original)
        info = infos.get(ref.archive)
        if sel.media and media_dir is not None and info is not None and is_plain_name(name):
            target = unique_media_target(Path(media_dir), name, info, taken)
            jobs.append((ref, target))
            mapping[ref.original] = target.as_posix()
        else:
            result.media_missing.append(ref.original)
    return jobs, mapping


def _rewritten_scene(zf: zipfile.ZipFile, name: str, mapping: dict[str, str]) -> str:
    try:
        data = json.loads(zf.read(name).decode("utf-8-sig"))
    except (ValueError, *ZIP_ERRORS) as e:
        raise InvalidBackupError(f"damaged scene collection in backup: {name}: {e}") from e
    return dump_scene_json(rewrite_paths(data, mapping))


def _unpack(zf: zipfile.ZipFile, name: str, dest: Path) -> None:
    """Write the member ``name`` to ``dest``; reading it checks its CRC."""
    try:
        with zf.open(name) as src, dest.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    except ZIP_ERRORS as e:
        raise InvalidBackupError(f"damaged file in backup: {name}: {e}") from e


def _check_names(sel: Selection) -> None:
    for name in [*sel.profiles, *sel.scene_collections]:
        if not is_plain_name(name):
            raise InvalidBackupError(f"unsafe name in backup: {name!r}")


def restore_backup(
    zip_path: Path,
    config_dir: Path,
    sel: Selection,
    media_dir: Path | None = None,
    progress: Progress | None = None,
) -> RestoreResult:
    """Restore the selected parts of a backup into ``config_dir``.

    OBS must not be running: it rewrites its scene collection and profile files
    when it exits and would overwrite the restored files.

    Every selected file is unpacked to a temporary folder inside ``config_dir``
    (which checks its CRC) before anything is replaced, so a damaged or unsafe
    backup leaves ``config_dir`` and ``media_dir`` as they were.

    Media: a file a restored scene collection uses is left alone if it still
    exists at its original path. Otherwise, if ``sel.media`` is set and the backup
    holds a copy, the copy goes to ``media_dir`` and the scene collection is
    changed to point there.
    """
    _check_names(sel)
    manifest = read_manifest(zip_path)
    config_dir = Path(config_dir)
    if media_dir is not None:
        # Scene collections need absolute paths; OBS resolves relative ones elsewhere.
        media_dir = Path(media_dir).absolute()
    result = RestoreResult(files=0)

    with zipfile.ZipFile(zip_path) as zf:
        infos = {info.filename: info for info in zf.infolist()}
        members = members_for(list(infos), sel)
        media_jobs, mapping = _plan_media(manifest, sel, media_dir, infos, result)

        # Check every path and scene collection before the first change.
        targets = {name: safe_target(config_dir, name[len(CONFIG_PREFIX) :]) for name in members}
        scenes: dict[str, str] = {}
        if mapping:
            scene_members = {f"{CONFIG_PREFIX}{_SCENES}/{f}" for f in sel.scene_collections}
            scenes = {
                name: _rewritten_scene(zf, name, mapping)
                for name in members
                if name in scene_members
            }
        profile_dirs = [
            safe_target(config_dir / obs_config.PROFILES_DIR, d)
            for d in sel.profiles
            if any(m.startswith(f"{CONFIG_PREFIX}{_PROFILES}/{d}/") for m in members)
        ]

        total = len(members) + len(media_jobs)
        created = not config_dir.is_dir()
        config_dir.mkdir(parents=True, exist_ok=True)
        # Inside config_dir, so the unpacked files can be moved into place by renaming.
        staging = Path(tempfile.mkdtemp(prefix=".restore-", dir=config_dir))
        try:
            # 1. Unpack everything; a damaged member stops the restore here.
            config_files: list[tuple[Path, Path]] = []  # (unpacked, final place)
            media_files: list[tuple[Path, Path]] = []
            for n, name in enumerate(members):
                if progress:
                    progress(n, total, name[len(CONFIG_PREFIX) :])
                unpacked = staging / str(n)
                if name in scenes:
                    unpacked.write_text(scenes[name], encoding="utf-8")
                else:
                    _unpack(zf, name, unpacked)
                config_files.append((unpacked, targets[name]))
            for n, (ref, target) in enumerate(media_jobs, len(members)):
                if progress:
                    progress(n, total, ref.original)
                if not target.exists():  # otherwise: the same file, restored before
                    _unpack(zf, ref.archive, staging / str(n))
                    media_files.append((staging / str(n), target))

            # 2. Replace. Profile folders are removed first, so files deleted
            # since the backup don't linger.
            for target in profile_dirs:
                if target.is_dir():
                    shutil.rmtree(target)
            for unpacked, target in config_files:
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(unpacked, target)
            for unpacked, target in media_files:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(unpacked, target)  # media_dir may be on another drive
        finally:
            shutil.rmtree(staging, ignore_errors=True)
            if created and not any(config_dir.iterdir()):
                config_dir.rmdir()  # nothing restored into a folder made for it
        result.files = len(config_files)
        result.media_restored = len(media_jobs)

    if progress:
        progress(total, total, "")
    return result


def restore_with_safety_backup(
    zip_path: Path,
    config_dir: Path,
    sel: Selection,
    media_dir: Path | None = None,
    safety_dir: Path | None = None,
    progress: Progress | None = None,
) -> RestoreResult:
    """``restore_backup``, after backing up the current config folder into ``safety_dir``.

    Without ``safety_dir`` no safety backup is made. If the restore fails after the
    safety backup was written, the error is a ``RestoreFailedError`` naming it.
    """
    config_dir = Path(config_dir)
    safety_path = None
    if safety_dir is not None and config_dir.is_dir():
        full = safety_selection(config_dir, sel)
        if not full.is_empty():
            safety_path = Path(safety_dir) / default_backup_name("_before-restore")
            create_backup(config_dir, safety_path, full, progress)
    try:
        result = restore_backup(zip_path, config_dir, sel, media_dir, progress)
    except Exception as e:
        if safety_path is None:
            raise
        raise RestoreFailedError(e, safety_path) from e
    result.safety_backup = safety_path
    return result
