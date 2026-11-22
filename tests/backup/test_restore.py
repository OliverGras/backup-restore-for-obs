"""Restoring backups, including media remapping and unsafe archives."""

import json
import zipfile
from pathlib import Path

import pytest

from obs_backup import backup
from obs_backup.backup import Selection

from support import everything, write


def test_restore_to_new_machine_remaps_missing_media(
    obs: Path, media: Path, tmp_path: Path
) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs))
    for f in media.iterdir():
        f.unlink()  # media gone, as on a new computer

    target = tmp_path / "new" / "obs-studio"
    media_dir = tmp_path / "restored media"
    sel = everything(obs)
    result = backup.restore_backup(dest, target, sel, media_dir)

    assert (
        target / "basic/profiles/Twitch_Stream/service.json"
    ).read_text() == '{"settings": {"key": "secret"}}'
    assert (target / "plugin_config/obs-browser/Cookies").is_file()
    assert result.media_restored == 2 and result.media_missing == []
    assert (media_dir / "logo.png").read_text() == "PNG"

    scene = json.loads((target / "basic/scenes/Main.json").read_text(encoding="utf-8"))
    settings = [s["settings"] for s in scene["sources"]]
    assert settings[0]["file"] == (media_dir / "logo.png").as_posix()
    assert settings[1]["local_file"] == (media_dir / "intro.mp4").as_posix()
    assert settings[2]["files"][0]["value"] == (media_dir / "logo.png").as_posix()
    assert settings[3]["url"] == "https://example.com/a.png"
    assert settings[4]["local_file"] == "C:/does/not/exist.mp4"


def test_restore_keeps_paths_when_media_exists(obs: Path, media: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs))
    target = tmp_path / "new"
    result = backup.restore_backup(dest, target, everything(obs), tmp_path / "m")
    assert result.media_restored == 0
    assert not (tmp_path / "m").exists()
    assert (target / "basic/scenes/Main.json").read_bytes() == (
        obs / "basic/scenes/Main.json"
    ).read_bytes()


def test_restore_reports_missing_media_without_option(
    obs: Path, media: Path, tmp_path: Path
) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs))
    for f in media.iterdir():
        f.unlink()
    sel = everything(obs, media=False)
    result = backup.restore_backup(dest, tmp_path / "new", sel)
    assert len(result.media_missing) == 2


def test_restore_replaces_profile_folder(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, Selection(profiles=["Twitch_Stream"]))
    write(obs / "basic/profiles/Twitch_Stream/stale.ini")
    write(obs / "basic/profiles/Twitch_Stream/basic.ini", "[General]\nName=Changed\n")
    backup.restore_backup(dest, obs, Selection(profiles=["Twitch_Stream"]))
    assert not (obs / "basic/profiles/Twitch_Stream/stale.ini").exists()
    assert "Twitch Stream" in (obs / "basic/profiles/Twitch_Stream/basic.ini").read_text()
    assert (obs / "basic/profiles/Unbenannt/basic.ini").exists()  # untouched


def test_restore_only_selected(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs, media=False))
    target = tmp_path / "new"
    backup.restore_backup(dest, target, Selection(scene_collections=["Other.json"]))
    files = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file())
    assert files == ["basic/scenes/Other.json"]


def test_rejects_zip_slip(tmp_path: Path) -> None:
    bad = tmp_path / "bad.zip"
    manifest = backup.Manifest("", "", "", None, "", [], [], True, False, False, False, [])
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("manifest.json", manifest.to_json())
        zf.writestr("config/plugin_manager/../../../evil.txt", "x")
    with pytest.raises(backup.InvalidBackupError):
        backup.restore_backup(bad, tmp_path / "cfg", Selection(global_settings=True))
    assert not (tmp_path / "evil.txt").exists()
