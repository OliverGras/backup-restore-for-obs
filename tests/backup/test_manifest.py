"""Reading manifests and listing backups."""

import zipfile
from pathlib import Path

import pytest

from obs_backup import backup
from obs_backup.backup import Selection


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
