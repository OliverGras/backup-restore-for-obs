"""Checkable tree of the things a backup can hold."""

from collections.abc import Iterator

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QWidget

from obs_backup.backup import Selection
from obs_backup.i18n import tr

ROLE_KIND = Qt.ItemDataRole.UserRole
ROLE_KEY = Qt.ItemDataRole.UserRole + 1

CHECKED = Qt.CheckState.Checked
UNCHECKED = Qt.CheckState.Unchecked


class SelectionTree(QTreeWidget):
    """Profiles and scene collections as groups, the other items as single entries."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setUniformRowHeights(True)

    def populate(
        self,
        profiles: list[tuple[str, str]],
        scenes: list[tuple[str, str]],
        global_settings: bool,
        plugin_config: bool,
        plugins: bool,
        browser: bool,
        browser_checked: bool = False,
    ) -> None:
        """Fill the tree. ``profiles`` and ``scenes`` are ``(display name, key)`` pairs."""
        self.blockSignals(True)
        self.clear()
        self._add_group("profiles", tr("item_profiles"), profiles)
        self._add_group("scenes", tr("item_scenes"), scenes)
        if global_settings:
            self._add_item("global", tr("item_global"), tr("item_global_hint"))
        if plugin_config:
            self._add_item("plugin_config", tr("item_plugin_config"), tr("item_plugin_config_hint"))
        if plugins:
            self._add_item("plugins", tr("item_plugins"), "")
        if browser:
            self._add_item("browser", tr("item_browser"), tr("item_browser_hint"), browser_checked)
        for col in (0, 1):
            self.resizeColumnToContents(col)
        self.blockSignals(False)

    def _add_group(self, kind: str, label: str, children: list[tuple[str, str]]) -> None:
        if not children:
            return
        parent = QTreeWidgetItem(self, [label, str(len(children))])
        parent.setData(0, ROLE_KIND, kind)
        parent.setFlags(
            parent.flags() | Qt.ItemFlag.ItemIsAutoTristate | Qt.ItemFlag.ItemIsUserCheckable
        )
        for name, key in children:
            child = QTreeWidgetItem(parent, [name, key if key != name else ""])
            child.setData(0, ROLE_KIND, kind)
            child.setData(0, ROLE_KEY, key)
            child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            child.setCheckState(0, CHECKED)
        parent.setExpanded(True)

    def _add_item(self, kind: str, label: str, hint: str, checked: bool = True) -> None:
        item = QTreeWidgetItem(self, [label, hint])
        item.setData(0, ROLE_KIND, kind)
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(0, CHECKED if checked else UNCHECKED)
        item.setToolTip(0, hint)

    def _top_items(self) -> Iterator[QTreeWidgetItem]:
        for i in range(self.topLevelItemCount()):
            if (item := self.topLevelItem(i)) is not None:
                yield item

    def set_all(self, checked: bool) -> None:
        state = CHECKED if checked else UNCHECKED
        for item in self._top_items():
            if item.childCount():
                for child in _children(item):
                    child.setCheckState(0, state)
            else:
                item.setCheckState(0, state)

    def selection(self) -> Selection:
        sel = Selection()
        for item in self._top_items():
            kind = item.data(0, ROLE_KIND)
            if item.childCount():
                keys = [
                    child.data(0, ROLE_KEY)
                    for child in _children(item)
                    if child.checkState(0) == CHECKED
                ]
                if kind == "profiles":
                    sel.profiles = keys
                elif kind == "scenes":
                    sel.scene_collections = keys
                continue
            on = item.checkState(0) == CHECKED
            if kind == "global":
                sel.global_settings = on
            elif kind == "plugin_config":
                sel.plugin_config = on
            elif kind == "plugins":
                sel.plugins = on
            elif kind == "browser":
                sel.browser_data = on
        return sel


def _children(item: QTreeWidgetItem) -> Iterator[QTreeWidgetItem]:
    for j in range(item.childCount()):
        if (child := item.child(j)) is not None:
            yield child


def selection_buttons(tree: SelectionTree) -> QWidget:
    """“Select all” and “Select none” buttons for a tree."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    for label, value in ((tr("select_all"), True), (tr("select_none"), False)):
        button = QPushButton(label)
        button.clicked.connect(lambda _=False, v=value: tree.set_all(v))
        layout.addWidget(button)
    layout.addStretch(1)
    return widget
