"""Small helpers for the user interface."""

from pathlib import Path

from PySide6.QtCore import QStandardPaths, QUrl
from PySide6.QtGui import QDesktopServices


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


def preview_list(items: list[str], limit: int = 10) -> str:
    """The first ``limit`` items, one per line, with "…" if there are more."""
    text = "\n".join(items[:limit])
    return text + "\n…" if len(items) > limit else text
