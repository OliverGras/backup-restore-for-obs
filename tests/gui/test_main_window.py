"""Smoke tests: the window builds, its parts are wired up, languages switch.

Skipped where Qt can't be loaded (e.g. a server without graphics libraries).
"""

from pathlib import Path

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtWidgets import QApplication  # noqa: E402

from obs_backup import backup  # noqa: E402
from obs_backup.gui.main_window import MainWindow  # noqa: E402
from obs_backup.gui.settings import AppSettings  # noqa: E402
from obs_backup.i18n import DEFAULT, LANGUAGES, set_language  # noqa: E402


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
    assert window.restore_tab._combo.currentData() == path
    assert window.restore_tab._manifest is not None


@pytest.mark.parametrize("code", sorted(LANGUAGES))
def test_switch_language(window: MainWindow, obs: Path, code: str) -> None:
    window.change_language(code)
    assert window.install.config_dir == obs
    assert window.backup_tab._tree.topLevelItemCount() == 5
