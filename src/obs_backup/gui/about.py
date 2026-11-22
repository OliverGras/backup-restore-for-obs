"""The About box."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QWidget

from obs_backup import __version__
from obs_backup.gui.constants import HOMEPAGE
from obs_backup.gui.licenses_dialog import LicensesDialog
from obs_backup.i18n import tr


def show_about(parent: QWidget) -> None:
    box = QMessageBox(
        QMessageBox.Icon.Information,
        tr("menu_about"),
        tr("about_text", version=__version__, homepage=HOMEPAGE),
        QMessageBox.StandardButton.NoButton,
        parent,
    )
    box.setTextFormat(Qt.TextFormat.RichText)
    box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
    licenses_button = box.addButton(tr("btn_licenses"), QMessageBox.ButtonRole.ActionRole)
    box.addButton(QMessageBox.StandardButton.Ok)
    box.exec()
    if box.clickedButton() is licenses_button:
        LicensesDialog(parent).exec()
