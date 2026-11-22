"""Restore a backup file into an OBS config folder."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

from obs_backup.backup.errors import InvalidBackupError
from obs_backup.backup.layout import CONFIG_PREFIX
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
    """``base / rel``, refusing paths that would end up outside ``base`` (zip slip)."""
    base = base.resolve()
    target = (base / rel).resolve()
    if target != base and base not in target.parents:
        raise InvalidBackupError(f"unsafe path in backup: {rel}")
    return target


def unique_media_target(media_dir: Path, name: str, size: int) -> Path:
    """A free file name in ``media_dir``; reuses a file of the same size (restored before)."""
    target = media_dir / name
    stem, suffix = target.stem, target.suffix
    n = 2
    while target.exists():
        if target.is_file() and target.stat().st_size == size:
            return target
        target = media_dir / f"{stem}_{n}{suffix}"
        n += 1
    return target


def _plan_media(
    manifest: Manifest,
    sel: Selection,
    media_dir: Path | None,
    archive_names: set[str],
    result: RestoreResult,
) -> tuple[list[tuple[MediaRef, Path]], dict[str, str]]:
    """Media files to extract, and the path rewrites for the scene collections."""
    jobs: list[tuple[MediaRef, Path]] = []
    mapping: dict[str, str] = {}
    for ref in manifest.media:
        if not set(ref.used_by) & set(sel.scene_collections):
            continue
        try:
            if Path(ref.original).is_file():
                continue  # still where the scene collection expects it
        except (OSError, ValueError):
            pass
        if sel.media and media_dir is not None and ref.archive in archive_names:
            target = unique_media_target(Path(media_dir), file_name(ref.original), ref.size)
            jobs.append((ref, target))
            mapping[ref.original] = target.as_posix()
        else:
            result.media_missing.append(ref.original)
    return jobs, mapping


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

    Media: a file a restored scene collection uses is left alone if it still
    exists at its original path. Otherwise, if ``sel.media`` is set and the backup
    holds a copy, the copy goes to ``media_dir`` and the scene collection is
    changed to point there.
    """
    manifest = read_manifest(zip_path)
    config_dir = Path(config_dir)
    result = RestoreResult(files=0)

    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        members = members_for(names, sel)
        scene_members = {f"{CONFIG_PREFIX}{_SCENES}/{f}" for f in sel.scene_collections}
        media_jobs, mapping = _plan_media(manifest, sel, media_dir, set(names), result)

        total = len(members) + len(media_jobs)
        done = 0
        config_dir.mkdir(parents=True, exist_ok=True)

        # Remove profile folders first, so files deleted since the backup don't linger.
        for d in sel.profiles:
            prefix = f"{CONFIG_PREFIX}{_PROFILES}/{d}/"
            if any(m.startswith(prefix) for m in members):
                target = safe_target(config_dir, f"{_PROFILES}/{d}")
                if target.is_dir():
                    shutil.rmtree(target)

        for name in members:
            rel = name[len(CONFIG_PREFIX) :]
            if progress:
                progress(done, total, rel)
            target = safe_target(config_dir, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            if name in scene_members and mapping:
                data = json.loads(zf.read(name).decode("utf-8-sig"))
                target.write_text(dump_scene_json(rewrite_paths(data, mapping)), encoding="utf-8")
            else:
                with zf.open(name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            result.files += 1
            done += 1

        for ref, target in media_jobs:
            if progress:
                progress(done, total, ref.original)
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(ref.archive) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
            result.media_restored += 1
            done += 1

    if progress:
        progress(total, total, "")
    return result
