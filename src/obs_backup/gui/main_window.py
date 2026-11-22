"""Main window: menus, the OBS installation panel, the two tabs and the status bar."""

from PySide6.QtCore import Slot
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent
from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QStyle,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from obs_backup import backup
from obs_backup.gui.about import show_about
from obs_backup.gui.backup_tab import BackupTab
from obs_backup.gui.constants import WINDOW_SIZE
from obs_backup.gui.helpers import open_folder, preview_list
from obs_backup.gui.install_panel import InstallPanel
from obs_backup.gui.restore_tab import RestoreTab
from obs_backup.gui.settings import AppSettings
from obs_backup.gui.tasks import LatestCall, TaskRunner
from obs_backup.i18n import LANGUAGES, current_language, set_language, tr


def error_message(error: BaseException) -> str:
    """The text shown for an error that a backup or restore raised."""
    if isinstance(error, backup.RestoreFailedError):
        return tr("restore_failed", error=error.reason, path=error.safety_backup)
    if isinstance(error, backup.IncompleteSafetyBackupError):
        return tr("safety_incomplete", count=len(error.skipped), files=preview_list(error.skipped))
    return tr("error_text", error=str(error) or type(error).__name__)


class MainWindow(QMainWindow):
    def __init__(self, settings: AppSettings | None = None) -> None:
        super().__init__()
        self._settings = settings or AppSettings()
        self._tasks = TaskRunner(self)
        self._tasks.started.connect(self._on_task_started)
        self._tasks.progress.connect(self._on_task_progress)
        self._tasks.ended.connect(self._on_task_ended)
        self._tasks.failed.connect(self._on_task_failed)
        # Counts media in the background; kept across language changes.
        self._media_counter = LatestCall(self)

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
        self.backup_tab = BackupTab(self._settings, self._tasks, self.install, self._media_counter)
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
        # A new menu bar: setMenuBar deletes the previous one with its menus and
        # actions, which clear() would leave behind after each language change.
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu(tr("menu_file"))
        file_menu.addAction(
            tr("menu_open_backup_dir"),
            lambda: open_folder(self._settings.backup_dir, create=True),
        )
        file_menu.addAction(tr("menu_open_config_dir"), self._open_config_dir)
        file_menu.addSeparator()
        file_menu.addAction(tr("menu_quit"), self.close)

        language_menu = menu_bar.addMenu(tr("menu_language"))
        group = QActionGroup(language_menu)
        for code, name in LANGUAGES.items():
            action = QAction(name, language_menu, checkable=True)
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
        # The config folder must not change while a task works on it.
        self.install.setEnabled(False)
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
        self.install.setEnabled(True)
        self._tabs.setEnabled(True)
        self.restore_tab.update_enabled()

    @Slot(object)
    def _on_task_failed(self, error: BaseException) -> None:
        QMessageBox.critical(self, tr("error_title"), error_message(error))

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 (Qt API)
        if self._tasks.busy:
            event.ignore()
            QMessageBox.information(self, tr("app_title"), tr("close_while_busy"))
            return
        self._media_counter.stop()
        super().closeEvent(event)
