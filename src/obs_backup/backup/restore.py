"""Restore a backup file into an OBS config folder."""

import errno
import json
import os
import shutil
import tempfile
import zipfile
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from obs_backup.backup.collect import browser_files, safety_selection
from obs_backup.backup.create import create_backup, new_backup_path
from obs_backup.backup.errors import (
    ZIP_ERRORS,
    BackupError,
    IncompleteSafetyBackupError,
    InvalidBackupError,
    RestoreFailedError,
)
from obs_backup.backup.layout import CONFIG_PREFIX, can_create, creatable_name, is_plain_name
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
    A backslash is part of a name here; on Windows ``can_create`` refuses it.

    The check is on the path as written, without resolving symlinks: a folder the
    user linked elsewhere (``basic/scenes`` in a synced folder) is restored into.
    A backup can't add symlinks, so the links followed are the user's own.
    """
    if "\0" in rel or any(part in ("", ".", "..") for part in rel.split("/")):
        raise InvalidBackupError("unsafe_path", path=rel)
    base = base.absolute()
    target = base / rel  # an absolute rel (C:/x on Windows) replaces base
    if base not in target.parents:
        raise InvalidBackupError("unsafe_path", path=rel)
    return target


def _config_target(config_dir: Path, name: str) -> Path:
    """Where the config member ``name`` goes; unsafe or impossible paths raise."""
    rel = name[len(CONFIG_PREFIX) :]
    target = safe_target(config_dir, rel)
    if not can_create(rel):
        raise InvalidBackupError("name_not_allowed", path=rel)
    return target


def _empty(folder: Path) -> None:
    """Remove everything in ``folder`` except the folders linked elsewhere.

    Backups don't follow links, so they don't hold what a linked folder contains,
    and a restore leaves such folders alone. ``folder`` itself may be a link.
    """
    for child in folder.iterdir():
        if not child.is_dir():
            child.unlink()
        elif not (child.is_symlink() or child.is_junction()):
            shutil.rmtree(child)


def _move(src: Path, dst: Path) -> None:
    """Move the unpacked file ``src`` to ``dst``, replacing the file there."""
    try:
        os.replace(src, dst)
    except OSError as e:
        if e.errno != errno.EXDEV:
            raise
        # dst is on another drive (a linked folder): copy it next to dst, then rename.
        tmp = dst.with_name(f".{dst.name}.restore-tmp")
        try:
            shutil.copyfile(src, tmp)
            os.replace(tmp, dst)
        except BaseException:
            tmp.unlink(missing_ok=True)
            raise
        src.unlink()


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
) -> tuple[list[tuple[MediaRef, Path]], dict[str, str], list[str]]:
    """Media files to extract, the path rewrites for the scene collections, and
    the media files that are missing and can't be restored."""
    jobs: list[tuple[MediaRef, Path]] = []
    mapping: dict[str, str] = {}
    missing: list[str] = []
    taken: set[Path] = set()
    for ref in manifest.media:
        if not set(ref.used_by) & set(sel.scene_collections):
            continue
        try:
            if Path(ref.original).is_file():
                continue  # still where the scene collection expects it
        except OSError, ValueError:
            pass
        name = creatable_name(file_name(ref.original))
        info = infos.get(ref.archive)
        if sel.media and media_dir is not None and info is not None and is_plain_name(name):
            target = unique_media_target(media_dir, name, info, taken)
            jobs.append((ref, target))
            mapping[ref.original] = target.as_posix()
        else:
            missing.append(ref.original)
    return jobs, mapping, missing


def _rewritten_scene(zf: zipfile.ZipFile, name: str, mapping: dict[str, str]) -> str:
    try:
        data = json.loads(zf.read(name).decode("utf-8-sig"))
    except (ValueError, *ZIP_ERRORS) as e:
        raise InvalidBackupError("damaged_scene", name=name, error=e) from e
    return dump_scene_json(rewrite_paths(data, mapping))


def _unpack(zf: zipfile.ZipFile, name: str, dest: Path) -> None:
    """Write the member ``name`` to ``dest``; reading it checks its CRC."""
    try:
        with zf.open(name) as src, dest.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    except ZIP_ERRORS as e:
        raise InvalidBackupError("damaged_file", name=name, error=e) from e


def _check_names(sel: Selection) -> None:
    for name in [*sel.profiles, *sel.scene_collections]:
        if not is_plain_name(name):
            raise InvalidBackupError("unsafe_name", name=name)


@dataclass
class _Plan:
    """What a restore will do, worked out and checked before anything changes."""

    targets: dict[str, Path]  # config member -> where it goes
    scenes: dict[str, str]  # config member -> scene collection with rewritten media paths
    emptied: list[Path]  # profile folders emptied before their files are restored
    stale: list[Path]  # browser data files removed before the backup's are restored
    media: list[tuple[MediaRef, Path]]  # media file -> where it goes
    media_missing: list[str]
    kept_current: list[str]  # selected files the backup lacks: the current ones stay


def _holds(rels: list[str], folder: str) -> bool:
    """Whether any of the config paths ``rels`` is inside ``folder``."""
    return any(r.startswith(f"{folder}/") for r in rels)


def _check_fits(target: Path, emptied: list[Path], removed: set[Path]) -> None:
    """Raise unless ``target`` can be written: no file or folder is in its way.

    Checked before anything changes, so that a folder where the backup has a file
    (or a file where it needs a folder) doesn't stop the restore halfway.
    """
    folders = target.parents
    if (outer := next((f for f in emptied if f in target.parents), None)) is not None:
        folders = [outer, *outer.parents]  # emptied first: only the folder itself counts
    elif target.is_dir():
        raise BackupError("folder_in_the_way", path=target)
    for folder in folders:
        if folder in removed:
            continue
        if folder.exists():
            if not folder.is_dir():
                raise BackupError("file_in_the_way", path=target, folder=folder)
            return


def _plan(
    zf: zipfile.ZipFile,
    manifest: Manifest,
    config_dir: Path,
    sel: Selection,
    media_dir: Path | None,
) -> _Plan:
    """Check every path and scene collection the restore will write."""
    infos = {info.filename: info for info in zf.infolist()}
    # Chosen by the names as stored. On Windows, zipfile turns a backslash into "/",
    # which would make "profiles/a\b/x" (from a Linux profile "a\b") a file of "a".
    members = members_for([info.orig_filename for info in zf.infolist()], sel)
    targets = {name: _config_target(config_dir, name) for name in members}
    media, mapping, media_missing = _plan_media(manifest, sel, media_dir, infos)
    scenes: dict[str, str] = {}
    if mapping:
        scene_members = {f"{CONFIG_PREFIX}{_SCENES}/{f}" for f in sel.scene_collections}
        scenes = {
            name: _rewritten_scene(zf, name, mapping) for name in members if name in scene_members
        }

    # A profile or the browser data replaces what is there only if the backup holds
    # all of it. Files that could not be read when the backup was made would be
    # lost otherwise; instead, the backup's files are restored over the current ones.
    # A backup made by an older version doesn't say which files it lacks: nothing
    # of it counts as complete, so restoring it removes no files.
    rels = [name[len(CONFIG_PREFIX) :] for name in members]
    skipped = manifest.skipped
    complete = {
        folder
        for folder in (*(f"{_PROFILES}/{d}" for d in sel.profiles), _BROWSER)
        if skipped is not None and _holds(rels, folder) and not _holds(skipped, folder)
    }
    emptied = [
        safe_target(config_dir / obs_config.PROFILES_DIR, d)
        for d in sel.profiles
        if f"{_PROFILES}/{d}" in complete
    ]
    # Chromium's databases must not meet journal or log files written after the backup.
    stale = browser_files(config_dir) if sel.browser_data and _BROWSER in complete else []

    removed = set(stale)
    for target in [*targets.values(), *(target for _, target in media)]:
        _check_fits(target, emptied, removed)
    return _Plan(
        targets=targets,
        scenes=scenes,
        emptied=emptied,
        stale=stale,
        media=media,
        media_missing=media_missing,
        kept_current=[rel for rel in skipped or [] if _is_selected(rel, sel)],
    )


def _apply(
    zf: zipfile.ZipFile, plan: _Plan, config_dir: Path, progress: Progress | None
) -> RestoreResult:
    """Unpack everything ``plan`` covers, then move it into place."""
    total = len(plan.targets) + len(plan.media)
    created = not config_dir.is_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    # Inside config_dir, so the unpacked files can be moved into place by renaming.
    staging = Path(tempfile.mkdtemp(prefix=".restore-", dir=config_dir))
    try:
        # 1. Unpack everything; a damaged member stops the restore here.
        moves: list[tuple[Path, Path]] = []  # (unpacked, final place)
        for n, (name, target) in enumerate(plan.targets.items()):
            if progress:
                progress(n, total, name[len(CONFIG_PREFIX) :])
            unpacked = staging / str(n)
            if name in plan.scenes:
                unpacked.write_text(plan.scenes[name], encoding="utf-8")
            else:
                _unpack(zf, name, unpacked)
            moves.append((unpacked, target))
        media_copied = 0
        for n, (ref, target) in enumerate(plan.media, len(plan.targets)):
            if progress:
                progress(n, total, ref.original)
            if not target.exists():  # otherwise: the same file, restored before
                _unpack(zf, ref.archive, staging / str(n))
                moves.append((staging / str(n), target))
                media_copied += 1

        # 2. Replace. Profile folders and browser data are cleared first, so files
        # deleted since the backup don't linger.
        for folder in plan.emptied:
            if folder.is_dir():
                _empty(folder)
        for path in plan.stale:
            path.unlink(missing_ok=True)
        for unpacked, target in moves:
            target.parent.mkdir(parents=True, exist_ok=True)
            _move(unpacked, target)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
        if created and not any(config_dir.iterdir()):
            config_dir.rmdir()  # nothing restored into a folder made for it
    if progress:
        progress(total, total, "")
    return RestoreResult(
        files=len(plan.targets),
        media_restored=media_copied,
        media_missing=plan.media_missing,
        kept_current=plan.kept_current,
    )


def _restore(
    zip_path: Path,
    config_dir: Path,
    sel: Selection,
    media_dir: Path | None,
    progress: Progress | None,
    before_changes: Callable[[], None] | None = None,
) -> RestoreResult:
    _check_names(sel)
    manifest = read_manifest(zip_path)
    # Absolute, so that the planned paths compare equal to the ones found on disk.
    config_dir = Path(config_dir).absolute()
    if media_dir is not None:
        # Scene collections need absolute paths; OBS resolves relative ones elsewhere.
        media_dir = Path(media_dir).absolute()
    with zipfile.ZipFile(zip_path) as zf:
        plan = _plan(zf, manifest, config_dir, sel, media_dir)
        if before_changes:
            before_changes()
        return _apply(zf, plan, config_dir, progress)


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

    Every path and scene collection is checked first. Then every selected file is
    unpacked to a temporary folder inside ``config_dir`` (which checks its CRC)
    before anything is replaced, so a damaged or unsafe backup leaves
    ``config_dir`` and ``media_dir`` as they were.

    Media: a file a restored scene collection uses is left alone if it still
    exists at its original path. Otherwise, if ``sel.media`` is set and the backup
    holds a copy, the copy goes to ``media_dir`` and the scene collection is
    changed to point there.
    """
    return _restore(zip_path, config_dir, sel, media_dir, progress)


def restore_with_safety_backup(
    zip_path: Path,
    config_dir: Path,
    sel: Selection,
    media_dir: Path | None = None,
    safety_dir: Path | None = None,
    progress: Progress | None = None,
) -> RestoreResult:
    """``restore_backup``, backing up the current config folder into ``safety_dir`` first.

    The safety backup is made once the backup to restore has passed its checks, so
    an unsafe or broken backup doesn't leave a needless safety backup behind.
    Without ``safety_dir`` no safety backup is made. If the safety backup can't
    read a file that the restore could replace or delete, it is deleted and
    ``IncompleteSafetyBackupError`` is raised before anything changes. If the
    restore fails after the safety backup was written, the error is a
    ``RestoreFailedError`` naming it.
    """
    config_dir = Path(config_dir)
    safety_path: Path | None = None

    def back_up_current_state() -> None:
        nonlocal safety_path
        if safety_dir is None or not config_dir.is_dir():
            return
        full = safety_selection(config_dir, sel)
        if full.is_empty():
            return
        path = new_backup_path(Path(safety_dir), "_before-restore")
        made = create_backup(config_dir, path, full, progress)
        # Unreadable files elsewhere don't matter: the restore leaves them alone.
        if at_risk := [rel for rel in made.skipped if _is_selected(rel, sel)]:
            path.unlink()
            raise IncompleteSafetyBackupError(at_risk)
        safety_path = path  # only once it exists

    try:
        result = _restore(zip_path, config_dir, sel, media_dir, progress, back_up_current_state)
    except Exception as e:
        if safety_path is None:
            raise
        raise RestoreFailedError(e, safety_path) from e
    result.safety_backup = safety_path
    return result
