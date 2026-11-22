"""Creating backups."""

import io
import os
import zipfile
from pathlib import Path
from typing import Any

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


def test_file_dated_before_1980_is_backed_up(obs: Path, tmp_path: Path) -> None:
    os.utime(obs / "global.ini", (0, 0))  # 1970: zip can't store dates before 1980
    dest = tmp_path / "b.zip"
    result = backup.create_backup(obs, dest, Selection(global_settings=True))
    assert not result.skipped
    assert "config/global.ini" in zipfile.ZipFile(dest).namelist()


class _FailsHalfway(io.RawIOBase):
    """A file that gives some data, then fails (as a region OBS holds locked would)."""

    def __init__(self) -> None:
        self._reads = 0

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Any) -> int:
        self._reads += 1
        if self._reads > 1:
            raise OSError("locked")
        buffer[:4] = b"half"
        return 4


def test_file_failing_halfway_is_left_out(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_open = Path.open

    def open_(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if self.name == "global.ini" and "b" in mode:
            return _FailsHalfway()
        return real_open(self, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", open_)
    dest = tmp_path / "b.zip"
    result = backup.create_backup(obs, dest, Selection(global_settings=True))
    names = zipfile.ZipFile(dest).namelist()
    assert result.skipped == ["global.ini"]
    assert "config/global.ini" not in names  # no truncated copy
    assert "config/user.ini" in names


def test_empty_selection_rejected(obs: Path, tmp_path: Path) -> None:
    with pytest.raises(backup.BackupError):
        backup.create_backup(obs, tmp_path / "b.zip", Selection(media=True))
