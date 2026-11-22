"""The selection tree turns ticked items into a backup.Selection."""

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtWidgets import QApplication  # noqa: E402

from obs_backup.gui.selection_tree import SelectionTree  # noqa: E402


@pytest.fixture
def tree() -> SelectionTree:
    if not isinstance(QApplication.instance(), QApplication):
        QApplication([])
    t = SelectionTree()
    t.populate(
        profiles=[("Twitch Stream", "Twitch_Stream"), ("YouTube", "YouTube")],
        scenes=[("Main", "Main.json")],
        global_settings=True,
        plugin_config=True,
        plugins=False,
        browser=True,
    )
    return t


def test_everything_but_browser_data_is_ticked_by_default(tree: SelectionTree) -> None:
    sel = tree.selection()
    assert sel.profiles == ["Twitch_Stream", "YouTube"]
    assert sel.scene_collections == ["Main.json"]
    assert sel.global_settings and sel.plugin_config
    assert not sel.browser_data and not sel.plugins


def test_select_none_and_all(tree: SelectionTree) -> None:
    tree.set_all(False)
    assert tree.selection().is_empty()
    tree.set_all(True)
    sel = tree.selection()
    assert sel.profiles == ["Twitch_Stream", "YouTube"] and sel.browser_data
