"""The manifest.json inside every backup, and finding backups."""

import json
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, TypedDict

from obs_backup.backup.errors import ZIP_ERRORS, InvalidBackupError
from obs_backup.backup.layout import (
    FORMAT,
    FORMAT_VERSION,
    MANIFEST,
    MEDIA_PREFIX,
    can_create,
    is_impossible_name,
    is_plain_name,
)
from obs_backup.backup.models import MediaRef


class ProfileEntry(TypedDict, closed=True):
    name: str  # profile name shown in OBS
    dir: str  # folder name under basic/profiles


class SceneCollectionEntry(TypedDict, closed=True):
    name: str  # scene collection name shown in OBS
    file: str  # file name under basic/scenes


@dataclass
class Manifest:
    created: str
    app_version: str
    source_os: str
    obs_version: str | None
    config_dir: str
    profiles: list[ProfileEntry]
    scene_collections: list[SceneCollectionEntry]
    global_settings: bool
    plugin_config: bool
    browser_data: bool
    plugins: bool
    media: list[MediaRef]
    # Config files (paths relative to the config folder) that could not be read
    # when the backup was made; a folder that could not be listed ends in "/".
    # The parts of the config folder they belong to are
    # restored over the current files instead of replacing them. None for backups
    # made by older versions, which didn't record them.
    skipped: list[str] | None = field(default_factory=list)
    format: str = FORMAT
    format_version: int = FORMAT_VERSION
    # Not stored: profile folders and scene collection files whose names this OS
    # can't use (a backup from Linux holding "a\b"). They are left out of
    # ``profiles`` and ``scene_collections``.
    unusable: list[str] = field(default_factory=list)

    def to_json(self) -> str:
        data = asdict(self)
        del data["unusable"]
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> Manifest:
        """Parse and check a manifest; anything malformed raises ``InvalidBackupError``.

        A manifest that loads is well-formed: every entry has the expected keys and
        types, and profile folders and scene collection files are plain names.
        Names that are fine on another OS but not on this one go to ``unusable``.
        """
        try:
            data = json.loads(text)
        except ValueError as e:
            raise InvalidBackupError("manifest_not_json", error=e) from e
        if not isinstance(data, dict) or data.get("format") != FORMAT:
            raise InvalidBackupError("not_a_backup")
        version = data.get("format_version", FORMAT_VERSION)
        if not _is_int(version):
            raise _damaged("format_version", version)
        if version > FORMAT_VERSION:
            raise InvalidBackupError("format_too_new", version=version, supported=FORMAT_VERSION)
        obs_version = data.get("obs_version")
        if obs_version is not None and not isinstance(obs_version, str):
            raise _damaged("obs_version", obs_version)
        unusable: list[str] = []
        return cls(
            created=_text(data, "created"),
            app_version=_text(data, "app_version"),
            source_os=_text(data, "source_os"),
            obs_version=obs_version,
            config_dir=_text(data, "config_dir"),
            profiles=[{"name": n, "dir": d} for n, d in _named(data, "profiles", "dir", unusable)],
            scene_collections=[
                {"name": n, "file": f}
                for n, f in _named(data, "scene_collections", "file", unusable)
            ],
            global_settings=_flag(data, "global_settings"),
            plugin_config=_flag(data, "plugin_config"),
            browser_data=_flag(data, "browser_data"),
            plugins=_flag(data, "plugins"),
            media=_media(data),
            skipped=_strings(data, "skipped") if "skipped" in data else None,
            format_version=version,
            unusable=unusable,
        )


def _damaged(key: str, value: object) -> InvalidBackupError:
    """The error for a manifest whose ``key`` holds ``value``, which it must not."""
    shown = repr(value)
    if len(shown) > 200:
        shown = shown[:200] + "…"
    return InvalidBackupError("manifest_damaged", field=key, value=shown)


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _text(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    if not isinstance(value, str):
        raise _damaged(key, value)
    return value


def _flag(data: dict[str, Any], key: str) -> bool:
    value = data.get(key, False)
    if not isinstance(value, bool):  # "false" would otherwise count as true
        raise _damaged(key, value)
    return value


def _list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise _damaged(key, value)
    return value


def _strings(data: dict[str, Any], key: str) -> list[str]:
    value = _list(data, key)
    if not all(isinstance(s, str) for s in value):
        raise _damaged(key, value)
    return value


def _named(
    data: dict[str, Any], key: str, name_key: str, unusable: list[str]
) -> list[tuple[str, str]]:
    """``(display name, folder or file name)`` of the profiles or scene collections.

    Names no OS has (``..``, ``a/b``) mean a damaged or crafted backup. Names this
    OS can't use are added to ``unusable`` and left out.
    """
    out = []
    for entry in _list(data, key):
        value = entry.get(name_key) if isinstance(entry, dict) else None
        if not isinstance(value, str) or is_impossible_name(value):
            raise _damaged(key, entry)
        if not (is_plain_name(value) and can_create(value)):
            unusable.append(value)
            continue
        name = entry.get("name")
        out.append((name if isinstance(name, str) and name else value, value))
    return out


def _media(data: dict[str, Any]) -> list[MediaRef]:
    refs = []
    for entry in _list(data, "media"):
        try:
            ref = MediaRef(**entry)
        except TypeError as e:
            raise _damaged("media", entry) from e
        if not (
            isinstance(ref.original, str)
            and ref.original
            and isinstance(ref.archive, str)
            and ref.archive.startswith(MEDIA_PREFIX)
            and _is_int(ref.size)
            and isinstance(ref.used_by, list)
            and all(isinstance(f, str) for f in ref.used_by)
        ):
            raise _damaged("media", entry)
        refs.append(ref)
    return refs


def read_manifest(path: Path) -> Manifest:
    try:
        with zipfile.ZipFile(path) as zf:
            text = zf.read(MANIFEST).decode("utf-8")
    except KeyError as e:
        raise InvalidBackupError("manifest_missing") from e
    except UnicodeDecodeError as e:
        raise InvalidBackupError("manifest_not_utf8", error=e) from e
    except ZIP_ERRORS as e:
        raise InvalidBackupError("not_a_zip", error=e) from e
    return Manifest.from_json(text)


def list_backups(folder: Path) -> list[tuple[Path, Manifest]]:
    """Valid backups in ``folder``, newest first."""
    if not folder.is_dir():
        return []
    found = []
    for f in folder.glob("*.zip", case_sensitive=False):  # also .ZIP on Linux
        try:  # stat() too: a file can vanish meanwhile, or be a broken link
            found.append((f.stat().st_mtime, f, read_manifest(f)))
        except InvalidBackupError, OSError:
            continue
    found.sort(key=lambda entry: entry[0], reverse=True)
    return [(f, m) for _, f, m in found]
