"""Creating backups."""

import io
import os
import socket
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

from obs_backup import backup
from obs_backup.backup import Selection, create

from support import everything, link, unreadable, write


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
    assert backup.read_manifest(dest).skipped == ["global.ini"]  # restore must know


def test_empty_selection_rejected(obs: Path, tmp_path: Path) -> None:
    with pytest.raises(backup.BackupError):
        backup.create_backup(obs, tmp_path / "b.zip", Selection(media=True))


def test_unreadable_media_file_is_left_out(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "b.zip"
    with unreadable(monkeypatch, "intro.mp4"):
        result = backup.create_backup(obs, dest, everything(obs))
    assert [Path(s).name for s in result.skipped] == ["intro.mp4"]
    assert [Path(r.original).name for r in backup.read_manifest(dest).media] == ["logo.png"]


def test_error_writing_the_backup_ends_it(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A full disk is not a file OBS holds open: the backup fails instead of skipping."""
    # The member being written; private, so not in the type stubs.
    write_file: Any = vars(zipfile)["_ZipWriteFile"]
    real_write = write_file.write

    def write_(self: Any, data: Any) -> int:
        if self._zinfo.filename == "config/user.ini":
            raise OSError(28, "No space left on device")
        return real_write(self, data)

    monkeypatch.setattr(write_file, "write", write_)
    dest = tmp_path / "b.zip"
    with pytest.raises(OSError, match="No space"):
        backup.create_backup(obs, dest, Selection(global_settings=True))
    assert not dest.exists() and not dest.with_name("b.zip.part").exists()


def test_existing_backup_is_never_replaced(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    dest.write_text("older backup")
    with pytest.raises(backup.BackupError, match="exists"):
        backup.create_backup(obs, dest, Selection(global_settings=True))
    assert dest.read_text() == "older backup"


def test_backup_being_written_is_left_alone(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    part = dest.with_name("b.zip.part")
    part.write_text("another backup, still being written")
    with pytest.raises(backup.BackupError, match="being written"):
        backup.create_backup(obs, dest, Selection(global_settings=True))
    assert part.read_text() == "another backup, still being written"


def test_backups_in_the_same_second_get_numbers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        create, "default_backup_name", lambda suffix="": f"obs-backup_T{suffix}.zip"
    )
    first = backup.new_backup_path(tmp_path)
    first.write_text("")
    second = backup.new_backup_path(tmp_path)
    second.with_name(second.name + ".part").write_text("")  # still being written
    third = backup.new_backup_path(tmp_path)
    assert [first.name, second.name, third.name] == [
        "obs-backup_T.zip",
        "obs-backup_T_2.zip",
        "obs-backup_T_3.zip",
    ]


def test_backup_taking_a_name_meanwhile_is_not_replaced(obs: Path, tmp_path: Path) -> None:
    """Another copy of the app may finish a backup of the same name first."""
    dest = tmp_path / "b.zip"

    def progress(done: int, total: int, current: str) -> None:
        if not dest.exists():
            dest.write_text("the other backup")

    with pytest.raises(backup.BackupError, match="exists"):
        backup.create_backup(obs, dest, Selection(global_settings=True), progress)
    assert dest.read_text() == "the other backup"
    assert not dest.with_name("b.zip.part").exists()


def test_folder_that_cannot_be_listed_counts_as_skipped(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write(obs / "basic/profiles/Twitch_Stream/sub/extra.ini")
    real_scandir = os.scandir

    def scandir(path: Any = ".") -> Any:
        if Path(path).name == "sub":
            raise PermissionError(13, "Access is denied", str(path))
        return real_scandir(path)

    monkeypatch.setattr(os, "scandir", scandir)
    dest = tmp_path / "b.zip"
    result = backup.create_backup(obs, dest, Selection(profiles=["Twitch_Stream"]))
    assert result.skipped == ["basic/profiles/Twitch_Stream/sub/"]
    assert backup.read_manifest(dest).skipped == ["basic/profiles/Twitch_Stream/sub/"]


# --- what counts as a file -------------------------------------------------------------


def test_linked_folders_inside_are_not_entered(obs: Path, tmp_path: Path) -> None:
    """Junctions too: os.walk follows them on Windows, and a loop never ends."""
    profile = obs / "basic/profiles/Twitch_Stream"
    link(profile / "overlays", write(tmp_path / "elsewhere" / "overlay.png").parent)
    link(profile / "loop", profile)
    dest = tmp_path / "b.zip"
    result = backup.create_backup(obs, dest, Selection(profiles=["Twitch_Stream"]))
    assert sorted(zipfile.ZipFile(dest).namelist()) == [
        "config/basic/profiles/Twitch_Stream/basic.ini",
        "config/basic/profiles/Twitch_Stream/service.json",
        "manifest.json",
    ]
    assert not result.skipped


def test_link_whose_target_is_gone_is_left_out(obs: Path, tmp_path: Path) -> None:
    """Not counted as unreadable: it holds nothing, and would block every safety backup."""
    gone = tmp_path / "gone"
    gone.mkdir()
    link(obs / "plugin_config/obs-browser/SingletonSocket", gone)
    gone.rmdir()
    dest = tmp_path / "b.zip"
    result = backup.create_backup(obs, dest, Selection(browser_data=True))
    assert not any("Singleton" in n for n in zipfile.ZipFile(dest).namelist())
    assert not result.skipped
    assert backup.read_manifest(dest).skipped == []


def test_socket_is_left_out(obs: Path, tmp_path: Path) -> None:
    if sys.platform == "win32":
        pytest.skip("POSIX sockets")
    with socket.socket(socket.AF_UNIX) as s:
        s.bind(str(obs / "plugin_config/obs-websocket/sock"))
        dest = tmp_path / "b.zip"
        result = backup.create_backup(obs, dest, Selection(plugin_config=True))
    assert "config/plugin_config/obs-websocket/sock" not in zipfile.ZipFile(dest).namelist()
    assert not result.skipped


def test_named_pipe_is_left_out(obs: Path, tmp_path: Path) -> None:
    """Opening a pipe nobody writes to would wait forever."""
    if sys.platform == "win32":
        pytest.skip("named pipes in the file system")
    os.mkfifo(obs / "plugin_config/obs-websocket/pipe")
    dest = tmp_path / "b.zip"
    result = backup.create_backup(obs, dest, Selection(plugin_config=True))
    assert "config/plugin_config/obs-websocket/pipe" not in zipfile.ZipFile(dest).namelist()
    assert not result.skipped


def test_file_name_that_is_not_utf8_is_skipped(obs: Path, tmp_path: Path) -> None:
    """Linux allows any bytes in a name; zip can only store UTF-8 names."""
    # How Python names the Linux file b"caf\xe9.ini"; Windows accepts the same name.
    name = os.fsdecode(b"caf\xe9.ini") if os.name != "nt" else "caf\udce9.ini"
    try:
        write(obs / "plugin_config/obs-websocket" / name)
    except OSError, UnicodeError:
        pytest.skip("this file system refuses the name")
    dest = tmp_path / "b.zip"
    seen: list[str] = []
    result = backup.create_backup(
        obs, dest, Selection(plugin_config=True), lambda d, t, cur: seen.append(cur)
    )
    shown = "plugin_config/obs-websocket/caf�.ini"
    assert result.skipped == [shown]
    assert backup.read_manifest(dest).skipped == [shown]
    assert "config/plugin_config/obs-websocket/config.json" in zipfile.ZipFile(dest).namelist()
    "".join(seen).encode("utf-8")  # the window can show every progress text
