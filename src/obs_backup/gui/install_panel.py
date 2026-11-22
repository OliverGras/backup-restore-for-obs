"""Top panel: which OBS config folder to use, and whether OBS is running."""

import html
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from obs_backup.gui.constants import BAD_COLOR, OK_COLOR, STATUS_INTERVAL_MS
from obs_backup.gui.settings import AppSettings
from obs_backup.gui.tasks import TaskRunner
from obs_backup.i18n import tr
from obs_backup.obs import config as obs_config
from obs_backup.obs.locator import (
    InstallKind,
    ObsInstallation,
    discover,
    running_obs_for,
    same_path,
)


class InstallPanel(QGroupBox):
    """Lists the OBS config folders found and checks regularly whether OBS is running."""

    config_dir_changed = Signal()
    running_changed = Signal(bool)

    def __init__(
        self, settings: AppSettings, tasks: TaskRunner, parent: QWidget | None = None
    ) -> None:
        super().__init__(tr("group_install"), parent)
        self._settings = settings
        self._tasks = tasks
        self._installs: list[ObsInstallation] = []
        self._running = False

        self._combo = QComboBox()
        self._combo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self._combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._combo.currentIndexChanged.connect(self._on_index_changed)

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(self._combo, 1)
        for label, slot in ((tr("btn_refresh"), self.refresh), (tr("btn_browse"), self._browse)):
            button = QPushButton(label)
            button.clicked.connect(slot)
            row_layout.addWidget(button)

        self._status = QLabel()
        self._status.setWordWrap(True)
        self._status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        form = QFormLayout(self)
        form.addRow(tr("install_label"), row)
        form.addRow(self._status)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update_status)
        self._timer.start(STATUS_INTERVAL_MS)
        self.refresh()

    @property
    def config_dir(self) -> Path | None:
        i = self._combo.currentIndex()
        return self._installs[i].config_dir if 0 <= i < len(self._installs) else None

    @property
    def obs_running(self) -> bool:
        return self._running

    def refresh(self) -> None:
        """Look for OBS installations again."""
        previous = self.config_dir or self._settings.last_config_dir
        self._installs = discover()
        custom = self._settings.custom_config_dir
        if custom and custom.is_dir() and not self._known(custom):
            self._installs.append(ObsInstallation(custom, InstallKind.CUSTOM))
        self._fill(previous)

    def _known(self, path: Path) -> bool:
        return any(same_path(i.config_dir, path) for i in self._installs)

    def _fill(self, select: Path | None) -> None:
        self._combo.blockSignals(True)
        self._combo.clear()
        index = 0
        for n, inst in enumerate(self._installs):
            extras = [tr(f"kind_{inst.kind}")]
            if inst.running:
                extras.append(tr("running_suffix"))
            if not inst.exists:
                extras.append(tr("not_found_suffix"))
            self._combo.addItem(f"{inst.config_dir}   ({', '.join(extras)})")
            if select and same_path(inst.config_dir, select):
                index = n
        self._combo.setCurrentIndex(index)
        self._combo.blockSignals(False)
        self._on_index_changed()

    def _browse(self) -> None:
        start = str(self.config_dir or Path.home())
        folder = QFileDialog.getExistingDirectory(self, tr("choose_config_dir"), start)
        if not folder:
            return
        path = Path(folder)
        if (
            not (path / "basic").is_dir()
            and QMessageBox.question(self, tr("not_obs_dir_title"), tr("not_obs_dir_text"))
            != QMessageBox.StandardButton.Yes
        ):
            return
        self._settings.custom_config_dir = path
        if not self._known(path):
            self._installs.append(ObsInstallation(path, InstallKind.CUSTOM))
        self._fill(path)

    def _on_index_changed(self, *_: object) -> None:
        if self.config_dir is None:
            return
        self._settings.last_config_dir = self.config_dir
        self.update_status()
        self.config_dir_changed.emit()

    def update_status(self) -> None:
        """Check whether OBS is running and show it, with the OBS version."""
        cfg = self.config_dir
        if cfg is None or self._tasks.busy:
            return
        proc = running_obs_for(cfg)
        parts = []
        if proc is not None:
            exe = str(proc.executable) if proc.executable else f"PID {proc.pid}"
            # The status is rich text: a path may hold "&" or "<".
            text = tr("status_running", exe=html.escape(exe))
            parts.append(f'<span style="color:{BAD_COLOR}">{text}</span>')
        else:
            parts.append(f'<span style="color:{OK_COLOR}">{tr("status_not_running")}</span>')
        version = obs_config.obs_version(cfg)
        if version:
            parts.append(tr("status_version", version=html.escape(version)))
        self._status.setText(" &nbsp; · &nbsp; ".join(parts))

        running = proc is not None
        if running != self._running:
            self._running = running
            self.running_changed.emit(running)
