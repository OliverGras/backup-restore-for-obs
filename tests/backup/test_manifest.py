"""Reading manifests and listing backups."""

import os
import zipfile
from pathlib import Path

import pytest

from obs_backup import backup
from obs_backup.backup import Selection
from obs_backup.backup.layout import is_plain_name

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
    "profiles is not a list": {"profiles": "Stream"},
    "profile without dir": {"profiles": [{"name": "Stream"}]},
    "profile is a string": {"profiles": ["Stream"]},
    "profile dir ..": {"profiles": [{"name": "x", "dir": ".."}]},
    "profile dir ../..": {"profiles": [{"name": "x", "dir": "../.."}]},
    "profile dir with slash": {"profiles": [{"name": "x", "dir": "a/b"}]},
    "scene file with backslash": {"scene_collections": [{"name": "x", "file": r"..\a.json"}]},
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


@pytest.mark.parametrize("name", ["", ".", "..", "a/b", r"a\b", "/abs", "a\0b"])
def test_names_that_are_not_plain(name: str) -> None:
    assert not is_plain_name(name)


@pytest.mark.skipif(os.name != "nt", reason="drive-relative paths exist only on Windows")
def test_drive_relative_name_is_not_plain() -> None:
    assert not is_plain_name("C:evil")
