"""Reading manifests and listing backups."""

import json
import os
import zipfile
from pathlib import Path

import pytest

from obs_backup import backup
from obs_backup.backup import Selection
from obs_backup.backup.layout import creatable_name, is_plain_name

from support import craft_backup


def test_rejects_foreign_zip(tmp_path: Path) -> None:
    z = tmp_path / "x.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("hello.txt", "x")
    with pytest.raises(backup.InvalidBackupError):
        backup.read_manifest(z)
    (tmp_path / "y.zip").write_text("not a zip")
    with pytest.raises(backup.InvalidBackupError):
        backup.read_manifest(tmp_path / "y.zip")


def test_list_backups(obs: Path, tmp_path: Path) -> None:
    folder = tmp_path / "backups"
    backup.create_backup(obs, folder / "a.zip", Selection(global_settings=True))
    (folder / "junk.zip").write_text("nope")
    assert [p.name for p, _ in backup.list_backups(folder)] == ["a.zip"]


# Each of these once escaped read_manifest as something other than InvalidBackupError,
# or loaded and then crashed the Restore tab or the restore itself.
DAMAGED = {
    "format_version is text": {"format_version": "x"},
    "format_version is null": {"format_version": None},
    "created is not text": {"created": 5},
    "flag is text": {"global_settings": "false"},
    "profiles is not a list": {"profiles": "Stream"},
    "profile without dir": {"profiles": [{"name": "Stream"}]},
    "profile is a string": {"profiles": ["Stream"]},
    "profile dir ..": {"profiles": [{"name": "x", "dir": ".."}]},
    "profile dir ../..": {"profiles": [{"name": "x", "dir": "../.."}]},
    "profile dir with slash": {"profiles": [{"name": "x", "dir": "a/b"}]},
    "scene file ..": {"scene_collections": [{"name": "x", "file": ".."}]},
    "skipped is not a list": {"skipped": "global.ini"},
    "skipped holds a number": {"skipped": [1]},
    "media is not an object": {"media": ["logo.png"]},
    "media with unknown key": {"media": [{"original": "/a.png", "evil": 1}]},
    "media outside media/": {"media": [{"original": "/a.png", "archive": "config/global.ini"}]},
    "media used_by not a list": {
        "media": [{"original": "/a.png", "archive": "media/0001_a.png", "used_by": "Main.json"}]
    },
}


@pytest.mark.parametrize("manifest", DAMAGED.values(), ids=DAMAGED.keys())
def test_rejects_damaged_manifest(tmp_path: Path, manifest: dict) -> None:
    path = craft_backup(tmp_path / "bad.zip", manifest)
    with pytest.raises(backup.InvalidBackupError):
        backup.read_manifest(path)


def test_rejects_manifest_that_is_not_utf8(tmp_path: Path) -> None:
    path = craft_backup(tmp_path / "bad.zip", b'{"format": "obs-backup", "created": "\xe9"}')
    with pytest.raises(backup.InvalidBackupError):
        backup.read_manifest(path)


def test_list_backups_skips_file_that_vanished(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "backups"
    backup.create_backup(obs, folder / "a.zip", Selection(global_settings=True))
    real_glob = Path.glob
    # As if gone.zip was deleted between listing the folder and reading it.
    monkeypatch.setattr(
        Path,
        "glob",
        lambda self, pattern, **kw: [*real_glob(self, pattern, **kw), self / "gone.zip"],
    )
    assert [p.name for p, _ in backup.list_backups(folder)] == ["a.zip"]


def test_list_backups_skips_damaged_manifests(obs: Path, tmp_path: Path) -> None:
    folder = tmp_path / "backups"
    backup.create_backup(obs, folder / "good.zip", Selection(global_settings=True))
    for i, manifest in enumerate(DAMAGED.values()):
        craft_backup(folder / f"bad{i}.zip", manifest)
    craft_backup(folder / "latin1.zip", b'{"format": "obs-backup", "created": "\xe9"}')
    assert [p.name for p, _ in backup.list_backups(folder)] == ["good.zip"]


def test_entries_always_have_name_and_folder(tmp_path: Path) -> None:
    path = craft_backup(
        tmp_path / "b.zip",
        {"profiles": [{"dir": "Stream"}], "scene_collections": [{"name": "", "file": "A.json"}]},
    )
    m = backup.read_manifest(path)
    assert m.profiles == [{"name": "Stream", "dir": "Stream"}]
    assert m.scene_collections == [{"name": "A.json", "file": "A.json"}]


@pytest.mark.parametrize(
    "name", ["Stream", "Main.json", "Szenen (alt)", "a:b" if os.name != "nt" else "a b"]
)
def test_plain_names(name: str) -> None:
    assert is_plain_name(name)


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", "/abs", "a\0b"])
def test_names_that_are_not_plain(name: str) -> None:
    assert not is_plain_name(name)


def test_backslash_separates_names_only_on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("obs_backup.backup.layout.WINDOWS", True)
    assert not is_plain_name(r"a\b") and not is_plain_name(r"..\a.json")
    if os.name != "nt":  # Linux and macOS allow a backslash in a name
        monkeypatch.setattr("obs_backup.backup.layout.WINDOWS", False)
        assert is_plain_name(r"a\b")


def test_names_this_system_cannot_use_are_left_out(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A backup from Linux stays usable on Windows, without what Windows can't hold."""
    monkeypatch.setattr("obs_backup.backup.layout.WINDOWS", True)
    path = craft_backup(
        tmp_path / "linux.zip",
        {
            "profiles": [{"dir": "Stream"}, {"dir": r"a\b"}, {"dir": "CON"}],
            "scene_collections": [{"file": "what?.json"}],
        },
    )
    m = backup.read_manifest(path)
    assert [p["dir"] for p in m.profiles] == ["Stream"] and m.scene_collections == []
    assert m.unusable == [r"a\b", "CON", "what?.json"]
    assert "unusable" not in json.loads(m.to_json())  # found when reading, not stored


@pytest.mark.parametrize(
    ("name", "windows", "expected"),
    [
        ("ok.png", True, "ok.png"),
        ("what?.png", True, "what_.png"),
        ('a<b>c:"d|e*.png', True, "a_b_c__d_e_.png"),
        ("trailing dot.", True, "trailing dot"),
        ("CON.png", True, "_CON.png"),
        ("...", True, "_"),
        ("what?.png", False, "what?.png"),  # Linux and macOS allow it
    ],
)
def test_creatable_name(
    monkeypatch: pytest.MonkeyPatch, name: str, windows: bool, expected: str
) -> None:
    monkeypatch.setattr("obs_backup.backup.layout.WINDOWS", windows)
    assert creatable_name(name) == expected


@pytest.mark.skipif(os.name != "nt", reason="drive-relative paths exist only on Windows")
def test_drive_relative_name_is_not_plain() -> None:
    assert not is_plain_name("C:evil")


def test_list_backups_finds_upper_case_extension(obs: Path, tmp_path: Path) -> None:
    folder = tmp_path / "backups"
    backup.create_backup(obs, folder / "OLD.ZIP", Selection(global_settings=True))
    assert [p.name for p, _ in backup.list_backups(folder)] == ["OLD.ZIP"]
