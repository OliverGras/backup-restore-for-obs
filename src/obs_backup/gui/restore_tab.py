"""“Restore” tab: pick a backup, choose what to restore and restore it."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from obs_backup import backup
from obs_backup.backup import Progress, RestoreResult
from obs_backup.gui.constants import BAD_COLOR
from obs_backup.gui.helpers import preview_list
from obs_backup.gui.install_panel import InstallPanel
from obs_backup.gui.selection_tree import SelectionTree, selection_buttons
from obs_backup.gui.settings import AppSettings
from obs_backup.gui.tasks import TaskRunner
from obs_backup.gui.widgets import FolderEdit
from obs_backup.i18n import tr
from obs_backup.obs.locator import running_obs_for


class RestoreTab(QWidget):
    restored = Signal()

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
        self._manifest: backup.Manifest | None = None

        self._combo = QComboBox()
        self._combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._combo.currentIndexChanged.connect(self._on_backup_selected)
        browse = QPushButton(tr("btn_browse"))
        browse.clicked.connect(self._browse_backup_file)
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self._combo, 1)
        row_layout.addWidget(browse)
        file_form = QFormLayout()
        file_form.addRow(tr("backup_file_label"), row)

        self._info = QLabel()
        self._info.setWordWrap(True)

        self._tree = SelectionTree()

        self._media_check = QCheckBox(tr("media_restore_checkbox"))
        self._media_check.setChecked(True)
        self._media_dir = FolderEdit(settings.media_dir, tr("choose_media_dir"))
        self._media_dir.changed.connect(self._on_media_dir_changed)
        media_form = QFormLayout()
        media_form.addRow(self._media_check, self._media_dir)

        self._safety_check = QCheckBox(tr("safety_checkbox"))
        self._safety_check.setChecked(True)

        self._hint = QLabel()
        self._hint.setStyleSheet(f"color: {BAD_COLOR}")

        self._button = QPushButton(tr("btn_restore"))
        self._button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self._button.setMinimumHeight(36)
        self._button.clicked.connect(self._start_restore)

        layout = QVBoxLayout(self)
        layout.addLayout(file_form)
        layout.addWidget(self._info)
        layout.addWidget(self._tree, 1)
        layout.addWidget(selection_buttons(self._tree))
        layout.addLayout(media_form)
        layout.addWidget(self._safety_check)
        layout.addWidget(self._hint)
        layout.addWidget(self._button)

    # ------------------------------------------------------------ choosing a backup

    def refresh_backups(self, select: Path | None = None) -> None:
        """List the backups in the backup folder; keep or set the selected one."""
        current = select or self._combo.currentData()
        self._combo.blockSignals(True)
        self._combo.clear()
        for path, _manifest in backup.list_backups(self._settings.backup_dir):
            self._combo.addItem(path.name, path)
        if current is not None:
            current = Path(current)
            index = self._combo.findData(current)
            if index < 0 and current.is_file():
                self._combo.insertItem(0, current.name, current)
                index = 0
            self._combo.setCurrentIndex(max(index, 0))
        self._combo.blockSignals(False)
        self._on_backup_selected()

    def _browse_backup_file(self) -> None:
        file, _ = QFileDialog.getOpenFileName(
            self, tr("choose_backup_file"), str(self._settings.backup_dir), tr("backup_filter")
        )
        if file:
            self.refresh_backups(select=Path(file))

    def _on_media_dir_changed(self, path: Path) -> None:
        self._settings.media_dir = path

    def _on_backup_selected(self, *_: object) -> None:
        self._manifest = None
        self._tree.clear()
        path = self._combo.currentData()
        if path is None:
            self._info.setText(tr("no_backups"))
            self.update_enabled()
            return
        try:
            m = backup.read_manifest(Path(path))
        except (backup.InvalidBackupError, OSError) as e:
            self._info.setText(tr("invalid_backup", error=e))
            self.update_enabled()
            return
        self._manifest = m
        self._info.setText(
            tr(
                "backup_info",
                created=m.created.replace("T", " ")[:19],
                os=m.source_os or tr("unknown"),
                obs=m.obs_version or tr("unknown"),
                media=len(m.media),
            )
        )
        self._tree.populate(
            profiles=[(p.get("name", p["dir"]), p["dir"]) for p in m.profiles],
            scenes=[(s.get("name", s["file"]), s["file"]) for s in m.scene_collections],
            global_settings=m.global_settings,
            plugin_config=m.plugin_config,
            plugins=m.plugins,
            browser=m.browser_data,
            browser_checked=True,
        )
        has_media = bool(m.media)
        self._media_check.setEnabled(has_media)
        self._media_dir.setEnabled(has_media)
        self.update_enabled()

    def update_enabled(self) -> None:
        """Allow restoring only with a valid backup, OBS closed and no task running."""
        running = self._install.obs_running
        self._hint.setText(tr("restore_blocked") if running else "")
        self._button.setEnabled(self._manifest is not None and not running and not self._tasks.busy)

    # ------------------------------------------------------------ restoring

    def _start_restore(self) -> None:
        cfg = self._install.config_dir
        path = self._combo.currentData()
        if cfg is None or path is None or self._manifest is None:
            return
        sel = self._tree.selection()
        if sel.is_empty():
            QMessageBox.information(self, tr("app_title"), tr("nothing_selected"))
            return
        if running_obs_for(cfg) is not None:
            QMessageBox.warning(self, tr("obs_running_title"), tr("obs_running_text"))
            self._install.update_status()
            return
        if (
            QMessageBox.question(
                self, tr("restore_confirm_title"), tr("restore_confirm_text", dir=cfg)
            )
            != QMessageBox.StandardButton.Yes
        ):
            return

        sel.media = self._media_check.isChecked() and bool(self._manifest.media)
        media_dir = self._media_dir.path() if sel.media else None
        safety = self._safety_check.isChecked()
        backup_dir = self._settings.backup_dir
        zip_path = Path(path)

        def task(progress: Progress) -> RestoreResult:
            safety_path = None
            if safety and cfg.is_dir():
                full = backup.full_selection(cfg)
                if not full.is_empty():
                    safety_path = backup_dir / backup.default_backup_name("_before-restore")
                    backup.create_backup(cfg, safety_path, full, progress)
            result = backup.restore_backup(zip_path, cfg, sel, media_dir, progress)
            result.safety_backup = safety_path
            return result

        self._tasks.run(tr("restore_running"), task, self._on_restore_done)

    def _on_restore_done(self, result: RestoreResult) -> None:
        text = tr("restore_done_text", files=result.files)
        if result.media_restored:
            text += tr(
                "restore_media_done", count=result.media_restored, dir=self._media_dir.path()
            )
        if result.media_missing:
            text += tr(
                "restore_media_missing",
                count=len(result.media_missing),
                files=preview_list(result.media_missing),
            )
        if result.safety_backup:
            text += tr("restore_safety_done", path=result.safety_backup)
        QMessageBox.information(self, tr("restore_done_title"), text)
        self.refresh_backups()
        self.restored.emit()
