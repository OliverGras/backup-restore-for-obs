import json
import zipfile
from pathlib import Path

import pytest

from obs_backup import archive
from obs_backup import obs_config as oc
from obs_backup.archive import Selection


def write(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def media(tmp_path: Path) -> Path:
    d = tmp_path / "media"
    write(d / "logo.png", "PNG")
    write(d / "intro.mp4", "MP4" * 100)
    return d


@pytest.fixture
def obs(tmp_path: Path, media: Path) -> Path:
    cfg = tmp_path / "obs-studio"
    write(cfg / "global.ini", "[General]\nLanguage=de-DE\n")
    write(cfg / "user.ini", "[Basic]\nProfile=Stream\n")
    write(cfg / "plugin_manager" / "modules.json", "{}")
    write(cfg / "basic/profiles/Twitch_Stream/basic.ini", "[General]\nName=Twitch Stream\n")
    write(cfg / "basic/profiles/Twitch_Stream/service.json", '{"settings": {"key": "secret"}}')
    write(cfg / "basic/profiles/Unbenannt/basic.ini", "[General]\nName=Unbenannt\n")
    scene = {
        "name": "Main Scenes",
        "sources": [
            {"id": "image_source", "settings": {"file": (media / "logo.png").as_posix()}},
            {"id": "ffmpeg_source", "settings": {"local_file": (media / "intro.mp4").as_posix()}},
            {"id": "slideshow", "settings": {"files": [{"value": (media / "logo.png").as_posix()}]}},
            {"id": "browser_source", "settings": {"url": "https://example.com/a.png"}},
            {"id": "ffmpeg_source", "settings": {"local_file": "C:/does/not/exist.mp4"}},
        ],
    }
    write(cfg / "basic/scenes/Main.json", json.dumps(scene))
    write(cfg / "basic/scenes/Main.json.bak", "{}")
    write(cfg / "basic/scenes/Other.json", json.dumps({"name": "Other", "sources": []}))
    write(cfg / "plugin_config/obs-websocket/config.json", '{"server_password": "pw"}')
    write(cfg / "plugin_config/obs-browser/Cookies", "cookies")
    write(cfg / "plugin_config/obs-browser/Cache/data_0", "cache")
    write(cfg / "plugin_config/obs-browser/LOCK", "")
    write(cfg / "logs/2026-11-22 08-59-11.txt", "08:59:11.491: OBS 33.0.1 (64-bit, windows)\n")
    write(cfg / "crashes/crash.txt")
    return cfg


def everything(cfg: Path, media: bool = True) -> Selection:
    sel = archive.full_selection(cfg)
    sel.browser_data = True
    sel.media = media
    return sel


def test_reads_config(obs: Path) -> None:
    assert [(p.name, p.dir_name) for p in oc.list_profiles(obs)] == [
        ("Twitch Stream", "Twitch_Stream"), ("Unbenannt", "Unbenannt")]
    assert [(s.name, s.file_name) for s in oc.list_scene_collections(obs)] == [
        ("Main Scenes", "Main.json"), ("Other", "Other.json")]
    assert oc.obs_version(obs) == "33.0.1"
    assert oc.has_plugin_config(obs) and oc.has_browser_data(obs) and not oc.has_plugins(obs)


def test_backup_contents(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "out" / "b.zip"
    result = archive.create_backup(obs, dest, everything(obs))
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
    assert sorted(n for n in names if n.startswith("media/")) == ["media/0001_logo.png", "media/0002_intro.mp4"]

    m = archive.read_manifest(dest)
    assert m.obs_version == "33.0.1"
    assert [p["dir"] for p in m.profiles] == ["Twitch_Stream", "Unbenannt"]
    assert len(m.media) == 2 and m.media[0].used_by == ["Main.json"]
    assert result.files == len(names) - 1 and not result.skipped
    assert not dest.with_name("b.zip.part").exists()


def test_backup_without_browser_and_media(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    archive.create_backup(obs, dest, archive.full_selection(obs))
    names = zipfile.ZipFile(dest).namelist()
    assert not any("obs-browser" in n or n.startswith("media/") for n in names)


def test_partial_selection(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    archive.create_backup(obs, dest, Selection(profiles=["Unbenannt"], scene_collections=["Other.json"]))
    names = set(zipfile.ZipFile(dest).namelist())
    assert names == {"manifest.json", "config/basic/profiles/Unbenannt/basic.ini", "config/basic/scenes/Other.json"}


def test_empty_selection_rejected(obs: Path, tmp_path: Path) -> None:
    with pytest.raises(archive.BackupError):
        archive.create_backup(obs, tmp_path / "b.zip", Selection(media=True))


def test_restore_to_new_machine_remaps_missing_media(obs: Path, media: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    archive.create_backup(obs, dest, everything(obs))
    for f in media.iterdir():
        f.unlink()  # media gone, as on a new computer

    target = tmp_path / "new" / "obs-studio"
    media_dir = tmp_path / "restored media"
    sel = everything(obs)
    result = archive.restore_backup(dest, target, sel, media_dir)

    assert (target / "basic/profiles/Twitch_Stream/service.json").read_text() == '{"settings": {"key": "secret"}}'
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
    archive.create_backup(obs, dest, everything(obs))
    target = tmp_path / "new"
    result = archive.restore_backup(dest, target, everything(obs), tmp_path / "m")
    assert result.media_restored == 0
    assert not (tmp_path / "m").exists()
    assert (target / "basic/scenes/Main.json").read_bytes() == (obs / "basic/scenes/Main.json").read_bytes()


def test_restore_reports_missing_media_without_option(obs: Path, media: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    archive.create_backup(obs, dest, everything(obs))
    for f in media.iterdir():
        f.unlink()
    sel = everything(obs, media=False)
    result = archive.restore_backup(dest, tmp_path / "new", sel)
    assert len(result.media_missing) == 2


def test_restore_replaces_profile_folder(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    archive.create_backup(obs, dest, Selection(profiles=["Twitch_Stream"]))
    write(obs / "basic/profiles/Twitch_Stream/stale.ini")
    write(obs / "basic/profiles/Twitch_Stream/basic.ini", "[General]\nName=Changed\n")
    archive.restore_backup(dest, obs, Selection(profiles=["Twitch_Stream"]))
    assert not (obs / "basic/profiles/Twitch_Stream/stale.ini").exists()
    assert "Twitch Stream" in (obs / "basic/profiles/Twitch_Stream/basic.ini").read_text()
    assert (obs / "basic/profiles/Unbenannt/basic.ini").exists()  # untouched


def test_restore_only_selected(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    archive.create_backup(obs, dest, everything(obs, media=False))
    target = tmp_path / "new"
    archive.restore_backup(dest, target, Selection(scene_collections=["Other.json"]))
    files = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file())
    assert files == ["basic/scenes/Other.json"]


def test_rejects_zip_slip(tmp_path: Path) -> None:
    bad = tmp_path / "bad.zip"
    manifest = archive.Manifest("", "", "", None, "", [], [], True, False, False, False, [])
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("manifest.json", manifest.to_json())
        zf.writestr("config/plugin_manager/../../../evil.txt", "x")
    with pytest.raises(archive.InvalidBackupError):
        archive.restore_backup(bad, tmp_path / "cfg", Selection(global_settings=True))
    assert not (tmp_path / "evil.txt").exists()


def test_rejects_foreign_zip(tmp_path: Path) -> None:
    z = tmp_path / "x.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("hello.txt", "x")
    with pytest.raises(archive.InvalidBackupError):
        archive.read_manifest(z)
    (tmp_path / "y.zip").write_text("not a zip")
    with pytest.raises(archive.InvalidBackupError):
        archive.read_manifest(tmp_path / "y.zip")


def test_list_backups(obs: Path, tmp_path: Path) -> None:
    folder = tmp_path / "backups"
    archive.create_backup(obs, folder / "a.zip", Selection(global_settings=True))
    (folder / "junk.zip").write_text("nope")
    assert [p.name for p, _ in archive.list_backups(folder)] == ["a.zip"]
