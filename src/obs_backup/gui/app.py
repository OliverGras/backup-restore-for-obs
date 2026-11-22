"""Start the application."""

from __future__ import annotations

import sys

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

from obs_backup import __version__
from obs_backup.gui.constants import APP, ORG
from obs_backup.gui.main_window import MainWindow
from obs_backup.gui.settings import AppSettings
from obs_backup.i18n import set_language, system_language


def run(argv: list[str] | None = None) -> int:
    app = QApplication(argv or sys.argv)
    app.setOrganizationName(ORG)
    app.setApplicationName(APP)
    app.setApplicationVersion(__version__)

    settings = AppSettings()
    set_language(settings.language or system_language(QLocale.system().name()))
    window = MainWindow(settings)
    window.show()
    return app.exec()
