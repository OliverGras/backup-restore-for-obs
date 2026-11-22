"""Smoke tests: the window builds, its parts are wired up, languages switch.

Skipped where Qt can't be loaded (e.g. a server without graphics libraries).
"""

import time
from pathlib import Path

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtCore import QCoreApplication, QEvent  # noqa: E402
from PySide6.QtGui import QActionGroup  # noqa: E402
from PySide6.QtWidgets import QApplication, QMenuBar, QMessageBox  # noqa: E402

from obs_backup import backup  # noqa: E402
from obs_backup.gui.helpers import documents_dir  # noqa: E402
from obs_backup.gui.main_window import MainWindow  # noqa: E402
from obs_backup.gui.settings import AppSettings  # noqa: E402
from obs_backup.gui.tasks import TaskRunner  # noqa: E402
from obs_backup.i18n import DEFAULT, LANGUAGES, set_language, tr  # noqa: E402

from support import craft_backup, everything  # noqa: E402


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


def test_media_counted_once_per_change(
    window: MainWindow, app: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = window.backup_tab
    tab._media_check.setChecked(True)
    scans: list[object] = []
    real_scan = backup.scan_media
    monkeypatch.setattr(backup, "scan_media", lambda *a: scans.append(a) or real_scan(*a))

    tab._tree.set_all(False)  # unchecks every profile and scene collection: many changes
    deadline = time.monotonic() + 5
    while not scans and time.monotonic() < deadline:
        app.processEvents()
    app.processEvents()
    assert len(scans) == 1
    assert tab._media_label.text().startswith("0 ")


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


def test_language_change_replaces_the_menus(window: MainWindow) -> None:
    for code in [*sorted(LANGUAGES), DEFAULT]:
        window.change_language(code)
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert len(window.findChildren(QActionGroup)) == 1
    assert len(window.findChildren(QMenuBar)) == 1


def test_close_while_busy_says_why(window: MainWindow, monkeypatch: pytest.MonkeyPatch) -> None:
    told: list[str] = []
    monkeypatch.setattr(TaskRunner, "busy", property(lambda self: True))
    monkeypatch.setattr(QMessageBox, "information", lambda parent, title, text: told.append(text))
    assert not window.close()
    assert told == [tr("close_while_busy")]


def test_media_options_off_for_backup_that_cannot_be_read(
    window: MainWindow, obs: Path, tmp_path: Path
) -> None:
    tab = window.restore_tab
    with_media = tmp_path / "with media.zip"
    backup.create_backup(obs, with_media, everything(obs))
    tab.refresh_backups(select=with_media)
    assert tab._media_check.isEnabled()

    tab.refresh_backups(select=craft_backup(tmp_path / "bad.zip", {"format_version": None}))
    assert not tab._media_check.isEnabled() and not tab._media_dir.isEnabled()
