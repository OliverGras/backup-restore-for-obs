"""Main window: menus, the OBS installation panel, the two tabs and the status bar."""

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from obs_backup.gui.about import show_about
from obs_backup.gui.backup_tab import BackupTab
from obs_backup.gui.constants import WINDOW_SIZE
from obs_backup.gui.helpers import open_folder
from obs_backup.gui.install_panel import InstallPanel
from obs_backup.gui.restore_tab import RestoreTab
from obs_backup.gui.settings import AppSettings
from obs_backup.gui.tasks import TaskRunner
from obs_backup.i18n import LANGUAGES, current_language, set_language, tr


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings | None = None) -> None:
        super().__init__()
        self._settings = settings or AppSettings()
        self._tasks = TaskRunner(self)
        self._tasks.started.connect(self._on_task_started)
        self._tasks.progress.connect(self._on_task_progress)
        self._tasks.ended.connect(self._on_task_ended)
        self._tasks.failed.connect(self._on_task_failed)

        self._progress = QProgressBar()
        self._progress.setMaximumWidth(260)
        self._progress.hide()
        self.statusBar().addPermanentWidget(self._progress)

        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon))
        self.resize(*WINDOW_SIZE)
        self._build_ui()

    def _build_ui(self) -> None:
        """Create menus and widgets in the current language (again after a language change)."""
        self.setWindowTitle(tr("app_title"))
        self._build_menu()

        self.install = InstallPanel(self._settings, self._tasks)
        self.backup_tab = BackupTab(self._settings, self._tasks, self.install)
        self.restore_tab = RestoreTab(self._settings, self._tasks, self.install)
        self._tabs = QTabWidget()
        self._tabs.addTab(self.backup_tab, tr("tab_backup"))
        self._tabs.addTab(self.restore_tab, tr("tab_restore"))

        self.install.config_dir_changed.connect(self._on_config_dir_changed)
        self.install.running_changed.connect(self.restore_tab.update_enabled)
        self.backup_tab.backup_created.connect(self.restore_tab.refresh_backups)
        self.backup_tab.backup_dir_changed.connect(self.restore_tab.refresh_backups)
        self.restore_tab.restored.connect(self.backup_tab.reload)
        self.restore_tab.restored.connect(self.install.update_status)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.install)
        layout.addWidget(self._tabs, 1)
        self.setCentralWidget(central)
        self._on_config_dir_changed()

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()
        menu_bar.clear()

        file_menu = menu_bar.addMenu(tr("menu_file"))
        file_menu.addAction(
            tr("menu_open_backup_dir"),
            lambda: open_folder(self._settings.backup_dir, create=True),
        )
        file_menu.addAction(tr("menu_open_config_dir"), self._open_config_dir)
        file_menu.addSeparator()
        file_menu.addAction(tr("menu_quit"), self.close)

        language_menu = menu_bar.addMenu(tr("menu_language"))
        group = QActionGroup(self)
        for code, name in LANGUAGES.items():
            action = QAction(name, self, checkable=True)
            action.setChecked(code == current_language())
            action.triggered.connect(lambda _=False, c=code: self.change_language(c))
            group.addAction(action)
            language_menu.addAction(action)

        help_menu = menu_bar.addMenu(tr("menu_help"))
        # "&" marks a shortcut letter in menus, so a literal "&" is written "&&".
        help_menu.addAction(tr("menu_about").replace("&", "&&"), lambda: show_about(self))

    def _open_config_dir(self) -> None:
        if self.install.config_dir is not None:
            open_folder(self.install.config_dir, create=True)

    def _on_config_dir_changed(self) -> None:
        self.backup_tab.reload()
        self.restore_tab.refresh_backups()

    def change_language(self, code: str) -> None:
        if code == current_language() or self._tasks.busy:
            return
        set_language(code)
        self._settings.language = code
        self._build_ui()
        self.statusBar().showMessage(tr("language_changed"), 3000)

    # ------------------------------------------------------------ background tasks

    @Slot(str)
    def _on_task_started(self, message: str) -> None:
        self._tabs.setEnabled(False)
        self.statusBar().showMessage(message)
        self._progress.setRange(0, 0)
        self._progress.show()

    @Slot(int, int, str)
    def _on_task_progress(self, done: int, total: int, current: str) -> None:
        self._progress.setRange(0, max(total, 1))
        self._progress.setValue(done)
        if current:
            self.statusBar().showMessage(current)

    @Slot()
    def _on_task_ended(self) -> None:
        self._progress.hide()
        self.statusBar().clearMessage()
        self._tabs.setEnabled(True)
        self.restore_tab.update_enabled()

    @Slot(str)
    def _on_task_failed(self, error: str) -> None:
        QMessageBox.critical(self, tr("error_title"), tr("error_text", error=error))

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt API)
        if self._tasks.busy:
            event.ignore()
            return
        super().closeEvent(event)
