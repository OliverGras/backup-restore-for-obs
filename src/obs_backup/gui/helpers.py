"""Small helpers for the user interface."""

from pathlib import Path

from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QDesktopServices

from obs_backup.backup.errors import BackupError, describe
from obs_backup.i18n import tr


def absolute_path(text: str) -> Path | None:
    """``text`` as a path, or None if it is empty or relative.

    A relative path would depend on the folder the app was started from, and OBS
    can't use relative media paths in scene collections.
    """
    path = Path(text.strip())
    return path if text.strip() and path.is_absolute() else None


def documents_dir() -> Path:
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    return Path(loc) if loc else Path.home()


def open_folder(path: Path, create: bool = False) -> None:
    """Show a folder in the system file manager."""
    if create:
        path.mkdir(parents=True, exist_ok=True)
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


def format_size(n: float) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def error_message(error: BaseException) -> str:
    """The message of ``error`` for the user: in their language if the app raised it."""
    if isinstance(error, BackupError):
        params = {
            k: error_message(v) if isinstance(v, BaseException) else v
            for k, v in error.params.items()
        }
        return tr(f"error_{error.code}", **params)
    return describe(error)
