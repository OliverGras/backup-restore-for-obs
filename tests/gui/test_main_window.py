"""Smoke tests: the window builds, its parts are wired up, languages switch.

Skipped where Qt can't be loaded (e.g. a server without graphics libraries).
"""

from pathlib import Path

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtWidgets import QApplication  # noqa: E402

from obs_backup import backup  # noqa: E402
from obs_backup.gui.helpers import documents_dir  # noqa: E402
from obs_backup.gui.main_window import MainWindow  # noqa: E402
from obs_backup.gui.settings import AppSettings  # noqa: E402
from obs_backup.i18n import DEFAULT, LANGUAGES, set_language  # noqa: E402

from support import craft_backup  # noqa: E402


@pytest.fixture
def app() -> QApplication:
    existing = QApplication.instance()
    return existing if isinstance(existing, QApplication) else QApplication([])


@pytest.fixture
def settings(tmp_path: Path, obs: Path) -> AppSettings:
    s = AppSettings(tmp_path / "settings.ini")
    s.backup_dir = tmp_path / "backups"
    s.custom_config_dir = obs
    s.last_config_dir = obs
    return s


@pytest.fixture
def window(app: QApplication, settings: AppSettings):
    w = MainWindow(settings)
    yield w
    w.close()
    set_language(DEFAULT)


def test_shows_the_chosen_obs_folder(window: MainWindow, obs: Path) -> None:
    assert window.install.config_dir == obs
    # profiles, scenes, general settings, plugin settings, browser data
    assert window.backup_tab._tree.topLevelItemCount() == 5


def test_new_backup_appears_in_restore_tab(
    window: MainWindow, settings: AppSettings, obs: Path
) -> None:
    path = settings.backup_dir / backup.default_backup_name()
    backup.create_backup(obs, path, backup.full_selection(obs))
    window.backup_tab.backup_created.emit(path)
    assert window.restore_tab.selected_backup() == path
    assert window.restore_tab._manifest is not None


def test_refresh_lists_each_backup_once(
    window: MainWindow, settings: AppSettings, obs: Path
) -> None:
    path = settings.backup_dir / backup.default_backup_name()
    backup.create_backup(obs, path, backup.full_selection(obs))
    window.backup_tab.backup_created.emit(path)
    window.restore_tab.refresh_backups()
    window.restore_tab.refresh_backups()
    assert window.restore_tab._combo.count() == 1
    assert window.restore_tab.selected_backup() == path


@pytest.mark.parametrize("text", ["", "  ", "relative/folder"])
def test_unusable_backup_folder_falls_back_to_default(
    window: MainWindow, settings: AppSettings, text: str
) -> None:
    folder = window.backup_tab._dir_edit
    folder._edit.setText(text)
    folder._edit.editingFinished.emit()
    assert settings.backup_dir == documents_dir() / "OBS Backups"
    assert folder.path() == settings.backup_dir  # the field shows the folder in use


def test_relative_folder_saved_earlier_counts_as_unset(tmp_path: Path) -> None:
    s = AppSettings(tmp_path / "settings.ini")
    s._qs.setValue("media_dir", ".")  # what older versions saved for an empty field
    assert s.media_dir == documents_dir() / "OBS Media"


@pytest.mark.parametrize("code", sorted(LANGUAGES))
def test_switch_language(window: MainWindow, obs: Path, code: str) -> None:
    window.change_language(code)
    assert window.install.config_dir == obs
    assert window.backup_tab._tree.topLevelItemCount() == 5


def test_starts_with_damaged_backups_in_the_folder(
    app: QApplication, settings: AppSettings
) -> None:
    craft_backup(settings.backup_dir / "bad.zip", {"format_version": None})
    craft_backup(settings.backup_dir / "latin1.zip", b'{"format": "obs-backup", "created": "\xe9"}')
    w = MainWindow(settings)
    try:
        assert w.restore_tab._combo.count() == 0
    finally:
        w.close()


def test_damaged_backup_cannot_be_restored(window: MainWindow, tmp_path: Path) -> None:
    path = craft_backup(tmp_path / "chosen.zip", {"profiles": [{"name": "no folder"}]})
    window.restore_tab.refresh_backups(select=path)
    assert window.restore_tab.selected_backup() == path
    assert window.restore_tab._manifest is None
    assert not window.restore_tab._button.isEnabled()
    assert window.restore_tab._tree.topLevelItemCount() == 0
