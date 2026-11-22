"""Work out which files a backup should contain."""

import os
from collections.abc import Callable
from pathlib import Path

from obs_backup.backup.models import MediaRef, Selection
from obs_backup.obs import config as obs_config
from obs_backup.obs.media import find_media_files, load_scene_json


def walk_files(
    root: Path,
    skip_dir: Callable[[str], bool] | None = None,
    skip_file: Callable[[str], bool] | None = None,
    unreadable: list[Path] | None = None,
) -> list[Path]:
    """All files under ``root`` (or ``root`` itself if it is a file), sorted.

    Linked folders inside ``root`` are not followed. Folders that can't be listed
    are added to ``unreadable``.
    """
    if root.is_file():
        return [root]
    if not root.is_dir():
        return []

    def note(error: OSError) -> None:
        if unreadable is not None and error.filename:
            unreadable.append(Path(error.filename))

    out = []
    for dirpath, dirnames, filenames in os.walk(root, onerror=note):
        if skip_dir:
            dirnames[:] = [d for d in dirnames if not skip_dir(d)]
        dirnames.sort()
        for name in sorted(filenames):
            if skip_file and skip_file(name):
                continue
            out.append(Path(dirpath) / name)
    return out


def _is_browser_cache_dir(name: str) -> bool:
    return name.lower() in obs_config.BROWSER_CACHE_DIRS


def _is_browser_skip_file(name: str) -> bool:
    name = name.lower()
    return name in obs_config.BROWSER_SKIP_FILES or name.endswith(".pma")


def browser_files(config_dir: Path, unreadable: list[Path] | None = None) -> list[Path]:
    """The browser data a backup holds: everything but caches and lock files."""
    return walk_files(
        config_dir / obs_config.BROWSER_DIR,
        skip_dir=_is_browser_cache_dir,
        skip_file=_is_browser_skip_file,
        unreadable=unreadable,
    )


def _children(folder: Path, unreadable: list[Path] | None) -> list[Path]:
    try:
        return sorted(folder.iterdir())
    except OSError:
        if unreadable is not None:
            unreadable.append(folder)
        return []


def collect_files(
    config_dir: Path, sel: Selection, unreadable: list[Path] | None = None
) -> list[Path]:
    """Files under ``config_dir`` that ``sel`` covers (without media).

    Folders that can't be listed are added to ``unreadable``; the files in them
    are missing from the list.
    """

    def walk(root: Path) -> list[Path]:
        return walk_files(root, unreadable=unreadable)

    # Python 3.15 allows [*walk(...) for d in ...] (PEP 798), but Pyright/Pylance
    # 1.1.414 still reports it as a syntax error, so nested comprehensions are used here.
    files = [path for d in sel.profiles for path in walk(config_dir / obs_config.PROFILES_DIR / d)]
    files += [
        path
        for f in sel.scene_collections
        if (path := config_dir / obs_config.SCENES_DIR / f).is_file()
    ]
    if sel.global_settings:
        files += [config_dir / f for f in obs_config.GLOBAL_FILES if (config_dir / f).is_file()]
        files += [path for d in obs_config.GLOBAL_DIRS for path in walk(config_dir / d)]
    if sel.plugin_config and (root := config_dir / obs_config.PLUGIN_CONFIG_DIR).is_dir():
        files += [
            path
            for child in _children(root, unreadable)
            if child.name != obs_config.BROWSER_DIR.name
            for path in walk(child)
        ]
    if sel.browser_data:
        files += browser_files(config_dir, unreadable)
    if sel.plugins:
        files += walk(config_dir / obs_config.PLUGINS_DIR)
    return files


def scan_media(config_dir: Path, scene_files: list[str]) -> list[MediaRef]:
    """Media files the given scene collections use and that exist on this machine."""
    refs: dict[str, MediaRef] = {}
    for f in scene_files:
        try:
            data = load_scene_json(config_dir / obs_config.SCENES_DIR / f)
        except OSError, ValueError:
            continue
        for path in find_media_files(data):
            ref = refs.get(path)
            if ref is None:
                try:
                    size = Path(path).stat().st_size
                except OSError:
                    continue
                ref = refs[path] = MediaRef(original=path, size=size)
            if f not in ref.used_by:
                ref.used_by.append(f)
    return list(refs.values())


def full_selection(config_dir: Path) -> Selection:
    """Everything worth keeping, except browser data (large, and rarely restored)."""
    return Selection(
        profiles=[p.dir_name for p in obs_config.list_profiles(config_dir)],
        scene_collections=[s.file_name for s in obs_config.list_scene_collections(config_dir)],
        global_settings=obs_config.has_global_settings(config_dir),
        plugin_config=obs_config.has_plugin_config(config_dir),
        plugins=obs_config.has_plugins(config_dir),
    )


def safety_selection(config_dir: Path, restoring: Selection) -> Selection:
    """What to back up before restoring ``restoring``: everything a restore can overwrite.

    Browser data (cookies, logins) is included only when it is about to be replaced.
    """
    sel = full_selection(config_dir)
    sel.browser_data = restoring.browser_data and obs_config.has_browser_data(config_dir)
    return sel
