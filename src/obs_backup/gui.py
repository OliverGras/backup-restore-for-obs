"""PySide6 user interface."""

from __future__ import annotations

import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from PySide6.QtCore import QObject, QSettings, QStandardPaths, Qt, QThread, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QAction, QActionGroup, QDesktopServices, QFontDatabase
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStyle,
    QTabWidget,
    QTextBrowser,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from obs_backup import __version__
from obs_backup import archive
from obs_backup import obs_config as oc
from obs_backup.legal import license_documents
from obs_backup.i18n import LANGUAGES, current_language, format_size, set_language, system_language, tr
from obs_backup.locator import ObsInstallation, discover, running_obs_for

ORG = "OBS Backup"
APP = "OBS Backup"
ROLE_KIND = Qt.ItemDataRole.UserRole
ROLE_KEY = Qt.ItemDataRole.UserRole + 1
OK_COLOR = "#2e9d4f"
BAD_COLOR = "#d9534f"


def documents_dir() -> Path:
    loc = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
    return Path(loc) if loc else Path.home()


def open_folder(path: Path) -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


class LicensesDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("licenses_title"))
        self.resize(860, 600)
        self.docs = license_documents()
        self.list = QListWidget()
        self.list.addItems([name for name, _ in self.docs])
        self.text = QTextBrowser()
        # Only web links open (in the browser); links to repo files mean nothing here.
        self.text.setOpenLinks(False)
        self.text.anchorClicked.connect(
            lambda url: url.scheme() in ("http", "https") and QDesktopServices.openUrl(url))
        splitter = QSplitter()
        splitter.addWidget(self.list)
        splitter.addWidget(self.text)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([240, 620])
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addWidget(splitter, 1)
        lay.addWidget(buttons)
        self.list.currentRowChanged.connect(self.show_doc)
        self.list.setCurrentRow(0)

    def show_doc(self, row: int) -> None:
        if 0 <= row < len(self.docs):
            path = self.docs[row][1]
            content = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix == ".md":
                self.text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont))
                self.text.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)
                self.text.setMarkdown(content)
            else:
                self.text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
                self.text.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)
                self.text.setPlainText(content)


# ---------------------------------------------------------------- background work


class Worker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, fn: Callable[[Callable[[int, int, str], None]], Any]):
        super().__init__()
        self._fn = fn

    @Slot()
    def run(self) -> None:
        try:
            result = self._fn(self.progress.emit)
        except Exception as e:  # noqa: BLE001 – shown to the user
            traceback.print_exc()
            self.failed.emit(str(e) or type(e).__name__)
        else:
            self.finished.emit(result)


# ---------------------------------------------------------------- selection tree


class SelectionTree(QTreeWidget):
    """Checkable tree of the things a backup can hold."""

    def __init__(self) -> None:
        super().__init__()
        self.setColumnCount(2)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)

    def populate(self, profiles: list[tuple[str, str]], scenes: list[tuple[str, str]],
                 global_settings: bool, plugin_config: bool, plugins: bool, browser: bool,
                 browser_checked: bool = False) -> None:
        """``profiles`` and ``scenes`` are ``(display name, key)`` pairs."""
        self.blockSignals(True)
        self.clear()

        def group(kind: str, label: str, children: list[tuple[str, str]]) -> None:
            if not children:
                return
            parent = QTreeWidgetItem(self, [label, str(len(children))])
            parent.setData(0, ROLE_KIND, kind)
            parent.setFlags(parent.flags() | Qt.ItemFlag.ItemIsAutoTristate | Qt.ItemFlag.ItemIsUserCheckable)
            for name, key in children:
                child = QTreeWidgetItem(parent, [name, key if key != name else ""])
                child.setData(0, ROLE_KIND, kind)
                child.setData(0, ROLE_KEY, key)
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Checked)
            parent.setExpanded(True)

        def single(kind: str, label: str, hint: str, checked: bool = True) -> None:
            item = QTreeWidgetItem(self, [label, hint])
            item.setData(0, ROLE_KIND, kind)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(0, Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            item.setToolTip(0, hint)

        group("profiles", tr("item_profiles"), profiles)
        group("scenes", tr("item_scenes"), scenes)
        if global_settings:
            single("global", tr("item_global"), tr("item_global_hint"))
        if plugin_config:
            single("plugin_config", tr("item_plugin_config"), tr("item_plugin_config_hint"))
        if plugins:
            single("plugins", tr("item_plugins"), "")
        if browser:
            single("browser", tr("item_browser"), tr("item_browser_hint"), browser_checked)
        for col in (0, 1):
            self.resizeColumnToContents(col)
        self.blockSignals(False)

    def set_all(self, checked: bool) -> None:
        state = Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.childCount():
                for j in range(item.childCount()):
                    item.child(j).setCheckState(0, state)
            else:
                item.setCheckState(0, state)

    def selection(self) -> archive.Selection:
        sel = archive.Selection()
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            kind = item.data(0, ROLE_KIND)
            if item.childCount():
                keys = [item.child(j).data(0, ROLE_KEY) for j in range(item.childCount())
                        if item.child(j).checkState(0) == Qt.CheckState.Checked]
                if kind == "profiles":
                    sel.profiles = keys
                elif kind == "scenes":
                    sel.scene_collections = keys
                continue
            on = item.checkState(0) == Qt.CheckState.Checked
            if kind == "global":
                sel.global_settings = on
            elif kind == "plugin_config":
                sel.plugin_config = on
            elif kind == "plugins":
                sel.plugins = on
            elif kind == "browser":
                sel.browser_data = on
        return sel


def path_row(edit: QLineEdit, on_browse: Callable[[], None]) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.addWidget(edit, 1)
    btn = QPushButton(tr("btn_browse"))
    btn.clicked.connect(on_browse)
    lay.addWidget(btn)
    return w


def select_buttons(tree: SelectionTree) -> QWidget:
    w = QWidget()
    lay = QHBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    for label, value in ((tr("select_all"), True), (tr("select_none"), False)):
        b = QPushButton(label)
        b.clicked.connect(lambda _=False, v=value: tree.set_all(v))
        lay.addWidget(b)
    lay.addStretch(1)
    return w


# ---------------------------------------------------------------- main window


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings(ORG, APP)
        self.installs: list[ObsInstallation] = []
        self.manifest: archive.Manifest | None = None
        self._thread: QThread | None = None
        self._worker: Worker | None = None
        self._on_done: Callable[[Any], None] | None = None
        self._obs_running = False

        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon))
        self.resize(820, 680)
        self._build_ui()
        self.refresh_installs()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_running_status)
        self.timer.start(3000)

    # ------------------------------------------------------------ settings

    @property
    def backup_dir(self) -> Path:
        return Path(self.settings.value("backup_dir", str(documents_dir() / "OBS Backups")))

    @property
    def media_dir(self) -> Path:
        return Path(self.settings.value("media_dir", str(documents_dir() / "OBS Media")))

    @property
    def config_dir(self) -> Path | None:
        i = self.install_combo.currentIndex()
        return self.installs[i].config_dir if 0 <= i < len(self.installs) else None

    # ------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        self.setWindowTitle(tr("app_title"))
        self._build_menu()

        central = QWidget()
        root = QVBoxLayout(central)

        # OBS installation
        box = QGroupBox(tr("group_install"))
        form = QFormLayout(box)
        self.install_combo = QComboBox()
        self.install_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.install_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.install_combo.currentIndexChanged.connect(self.on_install_changed)
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.install_combo, 1)
        for label, slot in ((tr("btn_refresh"), self.refresh_installs), (tr("btn_browse"), self.browse_config_dir)):
            b = QPushButton(label)
            b.clicked.connect(slot)
            rl.addWidget(b)
        form.addRow(tr("install_label"), row)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.status_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addRow(self.status_label)
        root.addWidget(box)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_backup_tab(), tr("tab_backup"))
        self.tabs.addTab(self._build_restore_tab(), tr("tab_restore"))
        root.addWidget(self.tabs, 1)

        self.setCentralWidget(central)

        self.progress = QProgressBar()
        self.progress.setMaximumWidth(260)
        self.progress.hide()
        self.statusBar().addPermanentWidget(self.progress)

    def _build_menu(self) -> None:
        mb = self.menuBar()
        mb.clear()
        file_menu = mb.addMenu(tr("menu_file"))
        file_menu.addAction(tr("menu_open_backup_dir"), lambda: self._open_dir(self.backup_dir))
        file_menu.addAction(tr("menu_open_config_dir"),
                            lambda: self.config_dir and self._open_dir(self.config_dir))
        file_menu.addSeparator()
        file_menu.addAction(tr("menu_quit"), self.close)

        lang_menu = mb.addMenu(tr("menu_language"))
        group = QActionGroup(self)
        for code, name in LANGUAGES.items():
            act = QAction(name, self, checkable=True)
            act.setChecked(code == current_language())
            act.triggered.connect(lambda _=False, c=code: self.change_language(c))
            group.addAction(act)
            lang_menu.addAction(act)

        help_menu = mb.addMenu(tr("menu_help"))
        help_menu.addAction(tr("menu_about"), self.show_about)

    def _build_backup_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        self.backup_tree = SelectionTree()
        self.backup_tree.itemChanged.connect(lambda *_: self.update_media_summary())
        lay.addWidget(self.backup_tree, 1)
        lay.addWidget(select_buttons(self.backup_tree))

        media_row = QHBoxLayout()
        self.media_check = QCheckBox(tr("media_checkbox"))
        self.media_check.setChecked(self.settings.value("include_media", False, type=bool))
        self.media_check.toggled.connect(self.update_media_summary)
        self.media_label = QLabel()
        media_row.addWidget(self.media_check)
        media_row.addStretch(1)
        media_row.addWidget(self.media_label)
        lay.addLayout(media_row)

        form = QFormLayout()
        self.backup_dir_edit = QLineEdit(str(self.backup_dir))
        self.backup_dir_edit.editingFinished.connect(
            lambda: self._set_backup_dir(Path(self.backup_dir_edit.text())))
        form.addRow(tr("backup_dir_label"), path_row(self.backup_dir_edit, self.browse_backup_dir))
        lay.addLayout(form)

        warn = QLabel(tr("secret_warning"))
        warn.setWordWrap(True)
        lay.addWidget(warn)

        self.backup_btn = QPushButton(tr("btn_backup"))
        self.backup_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton))
        self.backup_btn.setMinimumHeight(36)
        self.backup_btn.clicked.connect(self.start_backup)
        lay.addWidget(self.backup_btn)
        return w

    def _build_restore_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)

        form = QFormLayout()
        self.backup_combo = QComboBox()
        self.backup_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.backup_combo.currentIndexChanged.connect(self.on_backup_selected)
        row = QWidget()
        rl = QHBoxLayout(row)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(self.backup_combo, 1)
        b = QPushButton(tr("btn_browse"))
        b.clicked.connect(self.browse_backup_file)
        rl.addWidget(b)
        form.addRow(tr("backup_file_label"), row)
        lay.addLayout(form)

        self.backup_info = QLabel()
        self.backup_info.setWordWrap(True)
        lay.addWidget(self.backup_info)

        self.restore_tree = SelectionTree()
        lay.addWidget(self.restore_tree, 1)
        lay.addWidget(select_buttons(self.restore_tree))

        media_form = QFormLayout()
        self.restore_media_check = QCheckBox(tr("media_restore_checkbox"))
        self.restore_media_check.setChecked(True)
        self.media_dir_edit = QLineEdit(str(self.media_dir))
        self.media_dir_edit.editingFinished.connect(
            lambda: self.settings.setValue("media_dir", self.media_dir_edit.text()))
        self.media_dir_row = path_row(self.media_dir_edit, self.browse_media_dir)
        media_form.addRow(self.restore_media_check, self.media_dir_row)
        lay.addLayout(media_form)

        self.safety_check = QCheckBox(tr("safety_checkbox"))
        self.safety_check.setChecked(True)
        lay.addWidget(self.safety_check)

        self.restore_hint = QLabel()
        self.restore_hint.setStyleSheet(f"color: {BAD_COLOR}")
        lay.addWidget(self.restore_hint)

        self.restore_btn = QPushButton(tr("btn_restore"))
        self.restore_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton))
        self.restore_btn.setMinimumHeight(36)
        self.restore_btn.clicked.connect(self.start_restore)
        lay.addWidget(self.restore_btn)
        return w

    # ------------------------------------------------------------ installs

    def refresh_installs(self) -> None:
        previous = self.config_dir or Path(self.settings.value("config_dir", ""))
        self.installs = discover()
        custom = self.settings.value("custom_config_dir", "")
        if custom and Path(custom).is_dir() and not any(
                str(i.config_dir) == custom for i in self.installs):
            self.installs.append(ObsInstallation(Path(custom), "custom"))
        self._fill_install_combo(previous)

    def _fill_install_combo(self, select: Path | None) -> None:
        self.install_combo.blockSignals(True)
        self.install_combo.clear()
        index = 0
        for n, inst in enumerate(self.installs):
            extras = [tr(f"kind_{inst.kind}")]
            if inst.running:
                extras.append(tr("running_suffix"))
            if not inst.exists:
                extras.append(tr("not_found_suffix"))
            self.install_combo.addItem(f"{inst.config_dir}   ({', '.join(extras)})")
            if select and str(inst.config_dir) == str(select):
                index = n
        self.install_combo.setCurrentIndex(index)
        self.install_combo.blockSignals(False)
        self.on_install_changed()

    def browse_config_dir(self) -> None:
        start = str(self.config_dir or Path.home())
        d = QFileDialog.getExistingDirectory(self, tr("choose_config_dir"), start)
        if not d:
            return
        path = Path(d)
        if not (path / "basic").is_dir():
            if QMessageBox.question(self, tr("not_obs_dir_title"), tr("not_obs_dir_text")) \
                    != QMessageBox.StandardButton.Yes:
                return
        self.settings.setValue("custom_config_dir", str(path))
        if not any(str(i.config_dir) == str(path) for i in self.installs):
            self.installs.append(ObsInstallation(path, "custom"))
        self._fill_install_combo(path)

    def on_install_changed(self, *_: object) -> None:
        cfg = self.config_dir
        if cfg is None:
            return
        self.settings.setValue("config_dir", str(cfg))
        self.backup_tree.populate(
            profiles=[(p.name, p.dir_name) for p in oc.list_profiles(cfg)],
            scenes=[(s.name, s.file_name) for s in oc.list_scene_collections(cfg)],
            global_settings=any((cfg / f).is_file() for f in oc.GLOBAL_FILES),
            plugin_config=oc.has_plugin_config(cfg),
            plugins=oc.has_plugins(cfg),
            browser=oc.has_browser_data(cfg),
        )
        self.update_media_summary()
        self.update_running_status()
        self.refresh_backups()

    def update_running_status(self) -> None:
        cfg = self.config_dir
        if cfg is None or self.is_busy():
            return
        proc = running_obs_for(cfg)
        self._obs_running = proc is not None
        parts = []
        if proc is not None:
            exe = str(proc.executable) if proc.executable else f"PID {proc.pid}"
            parts.append(f'<span style="color:{BAD_COLOR}">{tr("status_running", exe=exe)}</span>')
        else:
            parts.append(f'<span style="color:{OK_COLOR}">{tr("status_not_running")}</span>')
        version = oc.obs_version(cfg)
        if version:
            parts.append(tr("status_version", version=version))
        self.status_label.setText(" &nbsp; · &nbsp; ".join(parts))
        self.update_restore_enabled()

    # ------------------------------------------------------------ backup

    def _set_backup_dir(self, path: Path) -> None:
        self.settings.setValue("backup_dir", str(path))
        self.backup_dir_edit.setText(str(path))
        self.refresh_backups()

    def browse_backup_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, tr("choose_backup_dir"), str(self.backup_dir))
        if d:
            self._set_backup_dir(Path(d))

    def update_media_summary(self) -> None:
        self.settings.setValue("include_media", self.media_check.isChecked())
        cfg = self.config_dir
        if not self.media_check.isChecked() or cfg is None:
            self.media_label.clear()
            return
        refs = archive.scan_media(cfg, self.backup_tree.selection().scene_collections)
        self.media_label.setText(tr("media_summary", count=len(refs),
                                    size=format_size(sum(r.size for r in refs))))

    def start_backup(self) -> None:
        cfg = self.config_dir
        sel = self.backup_tree.selection()
        sel.media = self.media_check.isChecked()
        if cfg is None or sel.is_empty():
            QMessageBox.information(self, tr("app_title"), tr("nothing_selected"))
            return
        if self._obs_running and QMessageBox.question(
                self, tr("obs_running_title"), tr("backup_while_running")) != QMessageBox.StandardButton.Yes:
            return
        self._set_backup_dir(Path(self.backup_dir_edit.text()))
        dest = self.backup_dir / archive.default_backup_name()
        self.run_task(tr("backup_running"),
                      lambda progress: archive.create_backup(cfg, dest, sel, progress),
                      self.on_backup_done)

    def on_backup_done(self, result: archive.BackupResult) -> None:
        text = tr("backup_done_text", files=result.files, size=format_size(result.total_bytes),
                  path=result.path)
        if result.skipped:
            text += tr("backup_skipped", count=len(result.skipped),
                       files="\n".join(result.skipped[:10]) + ("\n…" if len(result.skipped) > 10 else ""))
        box = QMessageBox(QMessageBox.Icon.Information, tr("backup_done_title"), text,
                          QMessageBox.StandardButton.NoButton, self)
        open_btn = box.addButton(tr("backup_open_folder"), QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Ok)
        box.exec()
        if box.clickedButton() is open_btn:
            open_folder(result.path.parent)
        self.refresh_backups(select=result.path)

    # ------------------------------------------------------------ restore

    def refresh_backups(self, select: Path | None = None) -> None:
        current = select or self.backup_combo.currentData()
        self.backup_combo.blockSignals(True)
        self.backup_combo.clear()
        for path, manifest in archive.list_backups(self.backup_dir):
            self.backup_combo.addItem(path.name, path)
        if current is not None:
            current = Path(current)
            idx = self.backup_combo.findData(current)
            if idx < 0 and current.is_file():
                self.backup_combo.insertItem(0, current.name, current)
                idx = 0
            self.backup_combo.setCurrentIndex(max(idx, 0))
        self.backup_combo.blockSignals(False)
        self.on_backup_selected()

    def browse_backup_file(self) -> None:
        f, _ = QFileDialog.getOpenFileName(self, tr("choose_backup_file"), str(self.backup_dir),
                                           tr("backup_filter"))
        if f:
            self.refresh_backups(select=Path(f))

    def browse_media_dir(self) -> None:
        d = QFileDialog.getExistingDirectory(self, tr("choose_media_dir"), self.media_dir_edit.text())
        if d:
            self.media_dir_edit.setText(d)
            self.settings.setValue("media_dir", d)

    def on_backup_selected(self, *_: object) -> None:
        self.manifest = None
        self.restore_tree.clear()
        path = self.backup_combo.currentData()
        if path is None:
            self.backup_info.setText(tr("no_backups"))
            self.update_restore_enabled()
            return
        try:
            m = archive.read_manifest(Path(path))
        except (archive.InvalidBackupError, OSError) as e:
            self.backup_info.setText(tr("invalid_backup", error=e))
            self.update_restore_enabled()
            return
        self.manifest = m
        self.backup_info.setText(tr(
            "backup_info", created=m.created.replace("T", " ")[:19], os=m.source_os or tr("unknown"),
            obs=m.obs_version or tr("unknown"), media=len(m.media)))
        self.restore_tree.populate(
            profiles=[(p.get("name", p["dir"]), p["dir"]) for p in m.profiles],
            scenes=[(s.get("name", s["file"]), s["file"]) for s in m.scene_collections],
            global_settings=m.global_settings,
            plugin_config=m.plugin_config,
            plugins=m.plugins,
            browser=m.browser_data,
            browser_checked=True,
        )
        has_media = bool(m.media)
        self.restore_media_check.setEnabled(has_media)
        self.media_dir_row.setEnabled(has_media)
        self.update_restore_enabled()

    def update_restore_enabled(self) -> None:
        if not hasattr(self, "restore_btn"):
            return
        self.restore_hint.setText(tr("restore_blocked") if self._obs_running else "")
        self.restore_btn.setEnabled(self.manifest is not None and not self._obs_running and not self.is_busy())

    def start_restore(self) -> None:
        cfg = self.config_dir
        path = self.backup_combo.currentData()
        if cfg is None or path is None or self.manifest is None:
            return
        sel = self.restore_tree.selection()
        if sel.is_empty():
            QMessageBox.information(self, tr("app_title"), tr("nothing_selected"))
            return
        if running_obs_for(cfg) is not None:
            QMessageBox.warning(self, tr("obs_running_title"), tr("obs_running_text"))
            self.update_running_status()
            return
        if QMessageBox.question(self, tr("restore_confirm_title"), tr("restore_confirm_text", dir=cfg)) \
                != QMessageBox.StandardButton.Yes:
            return

        sel.media = self.restore_media_check.isChecked() and bool(self.manifest.media)
        media_dir = Path(self.media_dir_edit.text()) if sel.media else None
        safety = self.safety_check.isChecked()
        backup_dir = self.backup_dir
        zip_path = Path(path)

        def task(progress: Callable[[int, int, str], None]) -> archive.RestoreResult:
            safety_path = None
            if safety and cfg.is_dir():
                full = archive.full_selection(cfg)
                if not full.is_empty():
                    safety_path = backup_dir / archive.default_backup_name("_before-restore")
                    archive.create_backup(cfg, safety_path, full, progress)
            result = archive.restore_backup(zip_path, cfg, sel, media_dir, progress)
            result.safety_backup = safety_path
            return result

        self.run_task(tr("restore_running"), task, self.on_restore_done)

    def on_restore_done(self, result: archive.RestoreResult) -> None:
        text = tr("restore_done_text", files=result.files)
        if result.media_restored:
            text += tr("restore_media_done", count=result.media_restored, dir=self.media_dir_edit.text())
        if result.media_missing:
            text += tr("restore_media_missing", count=len(result.media_missing),
                       files="\n".join(result.media_missing[:10])
                       + ("\n…" if len(result.media_missing) > 10 else ""))
        if result.safety_backup:
            text += tr("restore_safety_done", path=result.safety_backup)
        QMessageBox.information(self, tr("restore_done_title"), text)
        self.on_install_changed()

    # ------------------------------------------------------------ tasks

    def is_busy(self) -> bool:
        return self._thread is not None

    def run_task(self, message: str, fn: Callable, on_done: Callable[[Any], None]) -> None:
        if self.is_busy():
            return
        self.tabs.setEnabled(False)
        self.statusBar().showMessage(message)
        self.progress.setRange(0, 0)
        self.progress.show()

        thread = QThread(self)
        worker = Worker(fn)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        # Bound slots of this window run in the GUI thread (queued connection).
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_task_finished)
        worker.failed.connect(self._on_task_failed)
        self._thread, self._worker, self._on_done = thread, worker, on_done
        thread.start()

    @Slot(int, int, str)
    def _on_progress(self, done: int, total: int, current: str) -> None:
        self.progress.setRange(0, max(total, 1))
        self.progress.setValue(done)
        if current:
            self.statusBar().showMessage(current)

    @Slot(object)
    def _on_task_finished(self, result: object) -> None:
        on_done = self._on_done
        self._task_ended()
        if on_done:
            on_done(result)

    @Slot(str)
    def _on_task_failed(self, error: str) -> None:
        self._task_ended()
        QMessageBox.critical(self, tr("error_title"), tr("error_text", error=error))

    def _task_ended(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
        self._thread = self._worker = self._on_done = None
        self.progress.hide()
        self.statusBar().clearMessage()
        self.tabs.setEnabled(True)
        self.update_restore_enabled()

    # ------------------------------------------------------------ misc

    def _open_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        open_folder(path)

    def change_language(self, code: str) -> None:
        if code == current_language():
            return
        set_language(code)
        self.settings.setValue("language", code)
        selected = self.config_dir
        self._build_ui()
        self._fill_install_combo(selected)
        self.statusBar().showMessage(tr("language_changed"), 3000)

    def show_about(self) -> None:
        box = QMessageBox(QMessageBox.Icon.Information, tr("menu_about"),
                          tr("about_text", version=__version__),
                          QMessageBox.StandardButton.NoButton, self)
        box.setTextFormat(Qt.TextFormat.RichText)
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        licenses_btn = box.addButton(tr("btn_licenses"), QMessageBox.ButtonRole.ActionRole)
        box.addButton(QMessageBox.StandardButton.Ok)
        box.exec()
        if box.clickedButton() is licenses_btn:
            LicensesDialog(self).exec()

    def closeEvent(self, event) -> None:  # noqa: N802 – Qt API
        if self.is_busy():
            event.ignore()
            return
        super().closeEvent(event)


def run(argv: list[str] | None = None) -> int:
    from PySide6.QtCore import QLocale

    app = QApplication(argv or sys.argv)
    app.setOrganizationName(ORG)
    app.setApplicationName(APP)
    app.setApplicationVersion(__version__)
    settings = QSettings(ORG, APP)
    set_language(settings.value("language", system_language(QLocale.system().name())))
    window = MainWindow()
    window.show()
    return app.exec()
