"""The manifest.json inside every backup, and finding backups."""

import json
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, TypedDict

from obs_backup.backup.errors import ZIP_ERRORS, InvalidBackupError
from obs_backup.backup.layout import FORMAT, FORMAT_VERSION, MANIFEST, MEDIA_PREFIX, is_plain_name
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
    format: str = FORMAT
    format_version: int = FORMAT_VERSION

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, text: str) -> Manifest:
        """Parse and check a manifest; anything malformed raises ``InvalidBackupError``.

        A manifest that loads is well-formed: every entry has the expected keys and
        types, and profile folders and scene collection files are plain names.
        """
        try:
            data = json.loads(text)
        except ValueError as e:
            raise InvalidBackupError(f"manifest.json is not valid JSON: {e}") from e
        if not isinstance(data, dict) or data.get("format") != FORMAT:
            raise InvalidBackupError("not a Backup & Restore for OBS archive")
        version = data.get("format_version", FORMAT_VERSION)
        if not _is_int(version):
            raise _damaged(f"format_version is {version!r}")
        if version > FORMAT_VERSION:
            raise InvalidBackupError(
                f"backup format {version} is newer than this tool supports "
                f"({FORMAT_VERSION}); please update Backup & Restore for OBS"
            )
        obs_version = data.get("obs_version")
        if obs_version is not None and not isinstance(obs_version, str):
            raise _damaged(f"obs_version is {obs_version!r}")
        return cls(
            created=_text(data, "created"),
            app_version=_text(data, "app_version"),
            source_os=_text(data, "source_os"),
            obs_version=obs_version,
            config_dir=_text(data, "config_dir"),
            profiles=[{"name": n, "dir": d} for n, d in _named(data, "profiles", "dir")],
            scene_collections=[
                {"name": n, "file": f} for n, f in _named(data, "scene_collections", "file")
            ],
            global_settings=_flag(data, "global_settings"),
            plugin_config=_flag(data, "plugin_config"),
            browser_data=_flag(data, "browser_data"),
            plugins=_flag(data, "plugins"),
            media=_media(data),
            format_version=version,
        )


def _damaged(detail: str) -> InvalidBackupError:
    return InvalidBackupError(f"manifest.json is damaged: {detail}")


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _text(data: dict[str, Any], key: str) -> str:
    value = data.get(key, "")
    if not isinstance(value, str):
        raise _damaged(f"{key} is {value!r}")
    return value


def _flag(data: dict[str, Any], key: str) -> bool:
    value = data.get(key, False)
    if not isinstance(value, bool):  # "false" would otherwise count as true
        raise _damaged(f"{key} is {value!r}")
    return value


def _list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key, [])
    if not isinstance(value, list):
        raise _damaged(f"{key} is not a list")
    return value


def _named(data: dict[str, Any], key: str, name_key: str) -> list[tuple[str, str]]:
    """``(display name, folder or file name)`` of the profiles or scene collections."""
    out = []
    for entry in _list(data, key):
        value = entry.get(name_key) if isinstance(entry, dict) else None
        if not isinstance(value, str) or not is_plain_name(value):
            raise _damaged(f"invalid entry in {key}: {entry!r}")
        name = entry.get("name")
        out.append((name if isinstance(name, str) and name else value, value))
    return out


def _media(data: dict[str, Any]) -> list[MediaRef]:
    refs = []
    for entry in _list(data, "media"):
        try:
            ref = MediaRef(**entry)
        except TypeError as e:
            raise _damaged(f"invalid media entry {entry!r}") from e
        if not (
            isinstance(ref.original, str)
            and ref.original
            and isinstance(ref.archive, str)
            and ref.archive.startswith(MEDIA_PREFIX)
            and _is_int(ref.size)
            and isinstance(ref.used_by, list)
            and all(isinstance(f, str) for f in ref.used_by)
        ):
            raise _damaged(f"invalid media entry {entry!r}")
        refs.append(ref)
    return refs


def read_manifest(path: Path) -> Manifest:
    try:
        with zipfile.ZipFile(path) as zf:
            text = zf.read(MANIFEST).decode("utf-8")
    except KeyError as e:
        raise InvalidBackupError(
            "manifest.json missing – not a Backup & Restore for OBS archive"
        ) from e
    except UnicodeDecodeError as e:
        raise InvalidBackupError(f"manifest.json is not valid UTF-8: {e}") from e
    except ZIP_ERRORS as e:
        raise InvalidBackupError(f"not a valid zip file: {e}") from e
    return Manifest.from_json(text)


def list_backups(folder: Path) -> list[tuple[Path, Manifest]]:
    """Valid backups in ``folder``, newest first."""
    if not folder.is_dir():
        return []
    found = []
    for f in folder.glob("*.zip"):
        try:  # stat() too: a file can vanish meanwhile, or be a broken link
            found.append((f.stat().st_mtime, f, read_manifest(f)))
        except InvalidBackupError, OSError:
            continue
    found.sort(key=lambda entry: entry[0], reverse=True)
    return [(f, m) for _, f, m in found]
