"""Creating backups."""

import zipfile
from pathlib import Path

import pytest

from obs_backup import backup
from obs_backup.backup import Selection

from support import everything


def test_backup_contents(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "out" / "b.zip"
    result = backup.create_backup(obs, dest, everything(obs))
    names = set(zipfile.ZipFile(dest).namelist())

    assert "config/global.ini" in names and "config/user.ini" in names
    assert "config/plugin_manager/modules.json" in names
    assert "config/basic/profiles/Twitch_Stream/service.json" in names
    assert "config/basic/scenes/Main.json" in names
    assert "config/basic/scenes/Main.json.bak" not in names
    assert "config/plugin_config/obs-websocket/config.json" in names
    assert "config/plugin_config/obs-browser/Cookies" in names
    assert not any("Cache" in n or n.endswith("LOCK") for n in names)
    assert not any(n.startswith(("config/logs", "config/crashes")) for n in names)
    assert sorted(n for n in names if n.startswith("media/")) == [
        "media/0001_logo.png",
        "media/0002_intro.mp4",
    ]

    m = backup.read_manifest(dest)
    assert m.obs_version == "33.0.1"
    assert [p["dir"] for p in m.profiles] == ["Twitch_Stream", "Unbenannt"]
    assert len(m.media) == 2 and m.media[0].used_by == ["Main.json"]
    assert result.files == len(names) - 1 and not result.skipped
    assert not dest.with_name("b.zip.part").exists()


def test_backup_without_browser_and_media(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, backup.full_selection(obs))
    names = zipfile.ZipFile(dest).namelist()
    assert not any("obs-browser" in n or n.startswith("media/") for n in names)


def test_partial_selection(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(
        obs, dest, Selection(profiles=["Unbenannt"], scene_collections=["Other.json"])
    )
    names = set(zipfile.ZipFile(dest).namelist())
    assert names == {
        "manifest.json",
        "config/basic/profiles/Unbenannt/basic.ini",
        "config/basic/scenes/Other.json",
    }


def test_empty_selection_rejected(obs: Path, tmp_path: Path) -> None:
    with pytest.raises(backup.BackupError):
        backup.create_backup(obs, tmp_path / "b.zip", Selection(media=True))
