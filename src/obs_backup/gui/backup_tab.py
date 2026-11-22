"""“Back up” tab: choose what to save and create the backup."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from obs_backup import backup
from obs_backup.gui.helpers import format_size, open_folder, preview_list
from obs_backup.gui.install_panel import InstallPanel
from obs_backup.gui.selection_tree import SelectionTree, selection_buttons
from obs_backup.gui.settings import AppSettings
from obs_backup.gui.tasks import TaskRunner
from obs_backup.gui.widgets import FolderEdit
from obs_backup.i18n import tr
from obs_backup.obs import config as obs_config


class BackupTab(QWidget):
    backup_created = Signal(Path)
    backup_dir_changed = Signal()

    def __init__(
        self,
        settings: AppSettings,
        tasks: TaskRunner,
        install: InstallPanel,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings
        self._tasks = tasks
        self._install = install

        self._tree = SelectionTree()
        self._tree.itemChanged.connect(lambda *_: self._update_media_summary())

        self._media_check = QCheckBox(tr("media_checkbox"))
        self._media_check.setChecked(settings.include_media)
        self._media_check.toggled.connect(self._on_media_toggled)
        self._media_label = QLabel()
        media_row = QHBoxLayout()
        media_row.addWidget(self._media_check)
        media_row.addStretch(1)
        media_row.addWidget(self._media_label)

        self._dir_edit = FolderEdit(settings.backup_dir, tr("choose_backup_dir"))
        self._dir_edit.changed.connect(self._on_dir_changed)
        form = QFormLayout()
        form.addRow(tr("backup_dir_label"), self._dir_edit)

        warning = QLabel(tr("secret_warning"))
        warning.setWordWrap(True)

        button = QPushButton(tr("btn_backup"))
        button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        button.setMinimumHeight(36)
        button.clicked.connect(self._start_backup)

        layout = QVBoxLayout(self)
        layout.addWidget(self._tree, 1)
        layout.addWidget(selection_buttons(self._tree))
        layout.addLayout(media_row)
        layout.addLayout(form)
        layout.addWidget(warning)
        layout.addWidget(button)

    def reload(self) -> None:
        """Show the contents of the currently selected OBS config folder."""
        cfg = self._install.config_dir
        if cfg is None:
            self._tree.clear()
            return
        self._tree.populate(
            profiles=[(p.name, p.dir_name) for p in obs_config.list_profiles(cfg)],
            scenes=[(s.name, s.file_name) for s in obs_config.list_scene_collections(cfg)],
            global_settings=any((cfg / f).is_file() for f in obs_config.GLOBAL_FILES),
            plugin_config=obs_config.has_plugin_config(cfg),
            plugins=obs_config.has_plugins(cfg),
            browser=obs_config.has_browser_data(cfg),
        )
        self._update_media_summary()

    def _on_media_toggled(self, checked: bool) -> None:
        self._settings.include_media = checked
        self._update_media_summary()

    def _update_media_summary(self) -> None:
        cfg = self._install.config_dir
        if not self._media_check.isChecked() or cfg is None:
            self._media_label.clear()
            return
        refs = backup.scan_media(cfg, self._tree.selection().scene_collections)
        size = format_size(sum(r.size for r in refs))
        self._media_label.setText(tr("media_summary", count=len(refs), size=size))

    def _on_dir_changed(self, path: Path | None) -> None:
        self._settings.backup_dir = path
        # An empty or relative entry falls back to the default folder; show which.
        self._dir_edit.set_path(self._settings.backup_dir)
        self.backup_dir_changed.emit()

    def _start_backup(self) -> None:
        cfg = self._install.config_dir
        sel = self._tree.selection()
        sel.media = self._media_check.isChecked()
        if cfg is None or sel.is_empty():
            QMessageBox.information(self, tr("app_title"), tr("nothing_selected"))
            return
        if (
            self._install.obs_running
            and QMessageBox.question(self, tr("obs_running_title"), tr("backup_while_running"))
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._on_dir_changed(self._dir_edit.path())
        dest = self._settings.backup_dir / backup.default_backup_name()
        self._tasks.run(
            tr("backup_running"),
            lambda progress: backup.create_backup(cfg, dest, sel, progress),
            self._on_backup_done,
        )

    def _on_backup_done(self, result: backup.BackupResult) -> None:
        size = format_size(result.total_bytes)
        text = tr("backup_done_text", files=result.files, size=size, path=result.path)
        if result.skipped:
            text += tr(
                "backup_skipped", count=len(result.skipped), files=preview_list(result.skipped)
            )
        box = QMessageBox(
            QMessageBox.Icon.Information,
            tr("backup_done_title"),
            text,
            QMessageBox.StandardButton.NoButton,
            self,
        )
        open_button = box.addButton(tr("backup_open_folder"), QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Ok)
        box.exec()
        if box.clickedButton() is open_button:
            open_folder(result.path.parent)
        self.backup_created.emit(result.path)
