"""Create and restore OBS backup archives.

A backup is a plain zip file::

    manifest.json          what the backup holds (see ``Manifest``)
    config/...             files from the OBS config folder, same relative layout
    media/0001_logo.png    optional copies of media files the scene collections use
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from obs_backup import __version__
from obs_backup import obs_config as oc
from obs_backup.media import (
    dump_scene_json,
    file_name,
    find_media_files,
    load_scene_json,
    rewrite_paths,
)

FORMAT = "obs-backup"
FORMAT_VERSION = 1
MANIFEST = "manifest.json"
CONFIG_PREFIX = "config/"
MEDIA_PREFIX = "media/"

# Already-compressed formats are stored as they are; deflating them only costs time.
_STORED_SUFFIXES = {
    ".mp4", ".mkv", ".mov", ".webm", ".flv", ".avi", ".mp3", ".ogg", ".m4a", ".aac",
    ".opus", ".flac", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".7z",
}

Progress = Callable[[int, int, str], None]


class BackupError(Exception):
    pass


class InvalidBackupError(BackupError):
    pass


@dataclass
class Selection:
    """What to back up or restore."""
    profiles: list[str] = field(default_factory=list)           # profile folder names
    scene_collections: list[str] = field(default_factory=list)  # scene collection file names
    global_settings: bool = False
    plugin_config: bool = False
    browser_data: bool = False
    plugins: bool = False
    media: bool = False

    def is_empty(self) -> bool:
        return not (self.profiles or self.scene_collections or self.global_settings
                    or self.plugin_config or self.browser_data or self.plugins)


@dataclass
class MediaRef:
    original: str           # path exactly as stored in the scene collection
    archive: str = ""       # member name in the zip
    size: int = 0
    used_by: list[str] = field(default_factory=list)  # scene collection file names


@dataclass
class Manifest:
    created: str
    app_version: str
    source_os: str
    obs_version: str | None
    config_dir: str
    profiles: list[dict]
    scene_collections: list[dict]
    global_settings: bool
    plugin_config: bool
    browser_data: bool
    plugins: bool
    media: list[MediaRef]
    format: str = FORMAT
    format_version: int = FORMAT_VERSION

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> "Manifest":
        try:
            data = json.loads(text)
        except ValueError as e:
            raise InvalidBackupError(f"manifest.json is not valid JSON: {e}") from e
        if not isinstance(data, dict) or data.get("format") != FORMAT:
            raise InvalidBackupError("not an OBS Backup archive")
        if int(data.get("format_version", 0)) > FORMAT_VERSION:
            raise InvalidBackupError(
                f"backup format {data.get('format_version')} is newer than this tool supports "
                f"({FORMAT_VERSION}); please update OBS Backup")
        try:
            return cls(
                created=data.get("created", ""),
                app_version=data.get("app_version", ""),
                source_os=data.get("source_os", ""),
                obs_version=data.get("obs_version"),
                config_dir=data.get("config_dir", ""),
                profiles=list(data.get("profiles", [])),
                scene_collections=list(data.get("scene_collections", [])),
                global_settings=bool(data.get("global_settings")),
                plugin_config=bool(data.get("plugin_config")),
                browser_data=bool(data.get("browser_data")),
                plugins=bool(data.get("plugins")),
                media=[MediaRef(**m) for m in data.get("media", [])],
                format_version=int(data.get("format_version", FORMAT_VERSION)),
            )
        except (TypeError, ValueError) as e:
            raise InvalidBackupError(f"manifest.json is damaged: {e}") from e


@dataclass
class BackupResult:
    path: Path
    files: int
    total_bytes: int
    skipped: list[str] = field(default_factory=list)


@dataclass
class RestoreResult:
    files: int
    media_restored: int = 0
    media_missing: list[str] = field(default_factory=list)
    safety_backup: Path | None = None


# ---------------------------------------------------------------- collecting


def _walk_files(root: Path, skip_dir: Callable[[str], bool] | None = None,
                skip_file: Callable[[str], bool] | None = None) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.is_dir():
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        if skip_dir:
            dirnames[:] = [d for d in dirnames if not skip_dir(d)]
        dirnames.sort()
        for name in sorted(filenames):
            if skip_file and skip_file(name):
                continue
            out.append(Path(dirpath) / name)
    return out


def collect_files(config_dir: Path, sel: Selection) -> list[Path]:
    """Files under ``config_dir`` that ``sel`` covers (without media)."""
    files: list[Path] = []
    for d in sel.profiles:
        files += _walk_files(config_dir / oc.PROFILES_DIR / d)
    for f in sel.scene_collections:
        p = config_dir / oc.SCENES_DIR / f
        if p.is_file():
            files.append(p)
    if sel.global_settings:
        files += [config_dir / f for f in oc.GLOBAL_FILES if (config_dir / f).is_file()]
        for d in oc.GLOBAL_DIRS:
            files += _walk_files(config_dir / d)
    if sel.plugin_config:
        root = config_dir / oc.PLUGIN_CONFIG_DIR
        if root.is_dir():
            for child in sorted(root.iterdir()):
                if child.name != oc.BROWSER_DIR.name:
                    files += _walk_files(child)
    if sel.browser_data:
        files += _walk_files(
            config_dir / oc.BROWSER_DIR,
            skip_dir=lambda d: d.lower() in oc.BROWSER_CACHE_DIRS,
            skip_file=lambda f: f.lower() in oc.BROWSER_SKIP_FILES or f.lower().endswith(".pma"),
        )
    if sel.plugins:
        files += _walk_files(config_dir / oc.PLUGINS_DIR)
    return files


def scan_media(config_dir: Path, scene_files: list[str]) -> list[MediaRef]:
    """Media files the given scene collections use and that exist on this machine."""
    refs: dict[str, MediaRef] = {}
    for f in scene_files:
        try:
            data = load_scene_json(config_dir / oc.SCENES_DIR / f)
        except (OSError, ValueError):
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


# ---------------------------------------------------------------- backup


def default_backup_name(suffix: str = "") -> str:
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"obs-backup_{stamp}{suffix}.zip"


def create_backup(config_dir: Path, dest: Path, sel: Selection,
                  progress: Progress | None = None) -> BackupResult:
    config_dir = Path(config_dir)
    if not config_dir.is_dir():
        raise BackupError(f"OBS config folder not found: {config_dir}")
    if sel.is_empty():
        raise BackupError("nothing selected")

    files = collect_files(config_dir, sel)
    media = scan_media(config_dir, sel.scene_collections) if sel.media else []
    total = len(files) + len(media)
    result = BackupResult(path=dest, files=0, total_bytes=0)

    profiles = [p for p in oc.list_profiles(config_dir) if p.dir_name in sel.profiles]
    scenes = [s for s in oc.list_scene_collections(config_dir) if s.file_name in sel.scene_collections]

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
                except (PermissionError, OSError):
                    result.skipped.append(rel)
                done += 1

            written_media: list[MediaRef] = []
            for i, ref in enumerate(media, 1):
                ref.archive = f"{MEDIA_PREFIX}{i:04d}_{file_name(ref.original)}"
                if progress:
                    progress(done, total, ref.original)
                ctype = (zipfile.ZIP_STORED if Path(ref.original).suffix.lower() in _STORED_SUFFIXES
                         else zipfile.ZIP_DEFLATED)
                try:
                    zf.write(ref.original, ref.archive, compress_type=ctype)
                    written_media.append(ref)
                    result.files += 1
                    result.total_bytes += ref.size
                except (PermissionError, OSError):
                    result.skipped.append(ref.original)
                done += 1

            manifest = Manifest(
                created=datetime.now().astimezone().isoformat(timespec="seconds"),
                app_version=__version__,
                source_os=platform.system(),
                obs_version=oc.obs_version(config_dir),
                config_dir=str(config_dir),
                profiles=[{"name": p.name, "dir": p.dir_name} for p in profiles],
                scene_collections=[{"name": s.name, "file": s.file_name} for s in scenes],
                global_settings=sel.global_settings,
                plugin_config=sel.plugin_config,
                browser_data=sel.browser_data,
                plugins=sel.plugins,
                media=written_media,
            )
            zf.writestr(MANIFEST, manifest.to_json())
        os.replace(tmp, dest)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise
    if progress:
        progress(total, total, "")
    return result


def full_selection(config_dir: Path) -> Selection:
    """Everything worth keeping, as used for the safety backup before a restore."""
    return Selection(
        profiles=[p.dir_name for p in oc.list_profiles(config_dir)],
        scene_collections=[s.file_name for s in oc.list_scene_collections(config_dir)],
        global_settings=True,
        plugin_config=oc.has_plugin_config(config_dir),
        plugins=oc.has_plugins(config_dir),
    )


# ---------------------------------------------------------------- restore


def read_manifest(path: Path) -> Manifest:
    try:
        with zipfile.ZipFile(path) as zf:
            try:
                text = zf.read(MANIFEST).decode("utf-8")
            except KeyError as e:
                raise InvalidBackupError("manifest.json missing – not an OBS Backup archive") from e
    except zipfile.BadZipFile as e:
        raise InvalidBackupError(f"not a valid zip file: {e}") from e
    return Manifest.from_json(text)


def _members_for(names: list[str], sel: Selection) -> list[str]:
    cfg = [n for n in names if n.startswith(CONFIG_PREFIX) and not n.endswith("/")]
    browser = f"{CONFIG_PREFIX}{oc.BROWSER_DIR.as_posix()}/"
    plugin_cfg = f"{CONFIG_PREFIX}{oc.PLUGIN_CONFIG_DIR.as_posix()}/"
    out: list[str] = []
    for n in cfg:
        rel = n[len(CONFIG_PREFIX):]
        parts = rel.split("/")
        if parts[:2] == ["basic", "profiles"] and len(parts) > 3:
            if parts[2] in sel.profiles:
                out.append(n)
        elif parts[:2] == ["basic", "scenes"] and len(parts) == 3:
            if parts[2] in sel.scene_collections:
                out.append(n)
        elif rel in oc.GLOBAL_FILES or parts[0] in oc.GLOBAL_DIRS:
            if sel.global_settings:
                out.append(n)
        elif n.startswith(browser):
            if sel.browser_data:
                out.append(n)
        elif n.startswith(plugin_cfg):
            if sel.plugin_config:
                out.append(n)
        elif parts[0] == oc.PLUGINS_DIR.as_posix():
            if sel.plugins:
                out.append(n)
    return out


def _safe_target(base: Path, rel: str) -> Path:
    base = base.resolve()
    target = (base / rel).resolve()
    if target != base and base not in target.parents:
        raise InvalidBackupError(f"unsafe path in backup: {rel}")
    return target


def _unique_media_target(media_dir: Path, name: str, size: int) -> Path:
    target = media_dir / name
    stem, suffix = target.stem, target.suffix
    n = 2
    while target.exists():
        if target.is_file() and target.stat().st_size == size:
            return target  # same file restored before
        target = media_dir / f"{stem}_{n}{suffix}"
        n += 1
    return target


def restore_backup(zip_path: Path, config_dir: Path, sel: Selection,
                   media_dir: Path | None = None,
                   progress: Progress | None = None) -> RestoreResult:
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
        members = _members_for(zf.namelist(), sel)
        scene_members = {f"{CONFIG_PREFIX}{oc.SCENES_DIR.as_posix()}/{f}" for f in sel.scene_collections}

        # Media to extract, and the path rewrites that follow from it.
        media_jobs: list[tuple[MediaRef, Path]] = []
        mapping: dict[str, str] = {}
        archive_names = set(zf.namelist())
        for ref in manifest.media:
            if not set(ref.used_by) & set(sel.scene_collections):
                continue
            try:
                if Path(ref.original).is_file():
                    continue
            except (OSError, ValueError):
                pass
            if sel.media and media_dir is not None and ref.archive in archive_names:
                target = _unique_media_target(Path(media_dir), file_name(ref.original), ref.size)
                media_jobs.append((ref, target))
                mapping[ref.original] = target.as_posix()
            else:
                result.media_missing.append(ref.original)

        total = len(members) + len(media_jobs)
        done = 0
        config_dir.mkdir(parents=True, exist_ok=True)

        # Remove profile folders first, so files deleted since the backup don't linger.
        for d in sel.profiles:
            if any(m.startswith(f"{CONFIG_PREFIX}{oc.PROFILES_DIR.as_posix()}/{d}/") for m in members):
                target = _safe_target(config_dir, (oc.PROFILES_DIR / d).as_posix())
                if target.is_dir():
                    shutil.rmtree(target)

        for name in members:
            rel = name[len(CONFIG_PREFIX):]
            if progress:
                progress(done, total, rel)
            target = _safe_target(config_dir, rel)
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


def list_backups(folder: Path) -> list[tuple[Path, Manifest]]:
    """Valid backups in ``folder``, newest first."""
    if not folder.is_dir():
        return []
    out = []
    for f in sorted(folder.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            out.append((f, read_manifest(f)))
        except (InvalidBackupError, OSError):
            continue
    return out
