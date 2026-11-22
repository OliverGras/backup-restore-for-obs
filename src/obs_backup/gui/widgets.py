"""Reusable widgets."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLineEdit, QPushButton, QWidget

from obs_backup.i18n import tr


class FolderEdit(QWidget):
    """A folder path with a “Browse…” button. Emits ``changed`` when the user edits it."""

    changed = Signal(Path)

    def __init__(self, path: Path, dialog_title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._dialog_title = dialog_title
        self._edit = QLineEdit(str(path))
        self._edit.editingFinished.connect(lambda: self.changed.emit(self.path()))
        browse = QPushButton(tr("btn_browse"))
        browse.clicked.connect(self._browse)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._edit, 1)
        layout.addWidget(browse)

    def path(self) -> Path:
        return Path(self._edit.text())

    def set_path(self, path: Path) -> None:
        self._edit.setText(str(path))

    def _browse(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self._dialog_title, self._edit.text())
        if folder:
            self.set_path(Path(folder))
            self.changed.emit(self.path())
