"""Values the app remembers between starts."""

from pathlib import Path

from PySide6.QtCore import QSettings

from obs_backup.gui.constants import APP, ORG
from obs_backup.gui.helpers import absolute_path, documents_dir


class AppSettings:
    """Typed access to the app's QSettings (registry on Windows, a .conf file on Linux).

    ``ini_file`` stores the settings in that file instead (used by the tests).
    """

    def __init__(self, ini_file: Path | None = None) -> None:
        if ini_file is None:
            self._qs = QSettings(ORG, APP)
        else:
            self._qs = QSettings(str(ini_file), QSettings.Format.IniFormat)

    def _str(self, key: str) -> str:
        value = self._qs.value(key, "")
        return value if isinstance(value, str) else ""

    def _path(self, key: str) -> Path | None:
        # Relative values (such as "." saved by older versions) count as unset.
        return absolute_path(self._str(key))

    def _set_path(self, key: str, path: Path | None) -> None:
        self._qs.setValue(key, "" if path is None else str(path))

    @property
    def backup_dir(self) -> Path:
        return self._path("backup_dir") or documents_dir() / "OBS Backups"

    @backup_dir.setter
    def backup_dir(self, path: Path | None) -> None:
        """None (or a relative path) means the default folder."""
        self._set_path("backup_dir", path)

    @property
    def media_dir(self) -> Path:
        return self._path("media_dir") or documents_dir() / "OBS Media"

    @media_dir.setter
    def media_dir(self, path: Path | None) -> None:
        """None (or a relative path) means the default folder."""
        self._set_path("media_dir", path)

    @property
    def include_media(self) -> bool:
        return bool(self._qs.value("include_media", False, type=bool))

    @include_media.setter
    def include_media(self, value: bool) -> None:
        self._qs.setValue("include_media", value)

    @property
    def language(self) -> str | None:
        return self._str("language") or None

    @language.setter
    def language(self, code: str) -> None:
        self._qs.setValue("language", code)

    @property
    def last_config_dir(self) -> Path | None:
        return self._path("config_dir")

    @last_config_dir.setter
    def last_config_dir(self, path: Path | None) -> None:
        self._set_path("config_dir", path)

    @property
    def custom_config_dir(self) -> Path | None:
        return self._path("custom_config_dir")

    @custom_config_dir.setter
    def custom_config_dir(self, path: Path | None) -> None:
        self._set_path("custom_config_dir", path)

    def clear(self) -> None:
        self._qs.clear()
