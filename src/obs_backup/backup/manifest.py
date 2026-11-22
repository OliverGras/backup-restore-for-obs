"""The manifest.json inside every backup, and finding backups."""

from __future__ import annotations

import json
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from obs_backup.backup.errors import InvalidBackupError
from obs_backup.backup.layout import FORMAT, FORMAT_VERSION, MANIFEST
from obs_backup.backup.models import MediaRef


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
    def from_json(cls, text: str) -> Manifest:
        try:
            data = json.loads(text)
        except ValueError as e:
            raise InvalidBackupError(f"manifest.json is not valid JSON: {e}") from e
        if not isinstance(data, dict) or data.get("format") != FORMAT:
            raise InvalidBackupError("not a Backup & Restore for OBS archive")
        if int(data.get("format_version", 0)) > FORMAT_VERSION:
            raise InvalidBackupError(
                f"backup format {data.get('format_version')} is newer than this tool supports "
                f"({FORMAT_VERSION}); please update Backup & Restore for OBS"
            )
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


def read_manifest(path: Path) -> Manifest:
    try:
        with zipfile.ZipFile(path) as zf:
            try:
                text = zf.read(MANIFEST).decode("utf-8")
            except KeyError as e:
                raise InvalidBackupError(
                    "manifest.json missing – not a Backup & Restore for OBS archive"
                ) from e
    except zipfile.BadZipFile as e:
        raise InvalidBackupError(f"not a valid zip file: {e}") from e
    return Manifest.from_json(text)


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
