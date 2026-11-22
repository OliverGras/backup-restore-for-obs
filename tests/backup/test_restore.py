"""Restoring backups, including media remapping and unsafe archives."""

import errno
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any

import pytest

from obs_backup import backup
from obs_backup.backup import Selection
from obs_backup.backup.restore import safe_target

from support import corrupt_member, craft_backup, everything, replace_member, unreadable, write


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


def _files(folder: Path) -> list[str]:
    return sorted(p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file())


# --- crafted names must not reach outside their folder --------------------------------


@pytest.mark.parametrize("bad", ["..", "../..", "a/../.."])
def test_crafted_profile_name_cannot_delete_config(obs: Path, tmp_path: Path, bad: str) -> None:
    before = _files(obs)
    zip_path = craft_backup(
        tmp_path / "evil.zip", {}, {"config/basic/profiles/../../dummy.txt": "x"}
    )
    # Names passed in directly (not from the manifest, which rejects them anyway).
    with pytest.raises(backup.InvalidBackupError):
        backup.restore_backup(zip_path, obs, Selection(profiles=[bad]))
    assert _files(obs) == before


def test_safe_target_refuses_the_folder_itself(tmp_path: Path) -> None:
    for rel in (".", "", "a/..", "a/../b", "a//b", "./a"):
        with pytest.raises(backup.InvalidBackupError):
            safe_target(tmp_path, rel)
    assert safe_target(tmp_path, "a/b") == tmp_path / "a" / "b"


def test_member_cannot_climb_into_unselected_parts(obs: Path, tmp_path: Path) -> None:
    """A path that stays inside the config folder but leaves the selected profile."""
    zip_path = craft_backup(
        tmp_path / "evil.zip",
        {"profiles": [{"name": "Twitch Stream", "dir": "Twitch_Stream"}]},
        {
            "config/basic/profiles/Twitch_Stream/basic.ini": "[General]\n",
            "config/basic/profiles/Twitch_Stream/../../../plugins/evil.so": "x",
        },
    )
    before = _files(obs)
    with pytest.raises(backup.InvalidBackupError):
        backup.restore_backup(zip_path, obs, Selection(profiles=["Twitch_Stream"]))
    assert _files(obs) == before
    assert not (obs / "plugins").exists()


# --- backups from another OS -----------------------------------------------------------


@pytest.fixture
def on_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Apply Windows' file name rules, whatever OS the tests run on."""
    monkeypatch.setattr("obs_backup.backup.layout.WINDOWS", True)


@pytest.mark.usefixtures("on_windows")
@pytest.mark.parametrize("name", ["a?b.ini", "x:y.ini", "dot.", "CON", r"x\y.ini"])
def test_name_windows_refuses_stops_before_any_change(obs: Path, tmp_path: Path, name: str) -> None:
    zip_path = craft_backup(
        tmp_path / "linux.zip",
        {"profiles": [{"name": "Twitch Stream", "dir": "Twitch_Stream"}]},
        {
            "config/basic/profiles/Twitch_Stream/basic.ini": "[General]\n",
            f"config/basic/profiles/Twitch_Stream/{name}": "x",
        },
    )
    before = _files(obs)
    with pytest.raises(backup.InvalidBackupError, match="not allowed"):
        backup.restore_backup(zip_path, obs, Selection(profiles=["Twitch_Stream"]))
    assert _files(obs) == before


@pytest.mark.usefixtures("on_windows")
def test_media_name_windows_refuses_is_changed(tmp_path: Path) -> None:
    original = "/home/me/what?.png"
    zip_path = craft_backup(
        tmp_path / "linux.zip",
        {
            "scene_collections": [{"name": "Main", "file": "Main.json"}],
            "media": [
                {
                    "original": original,
                    "archive": "media/0001_what?.png",
                    "size": 3,
                    "used_by": ["Main.json"],
                }
            ],
        },
        {
            "config/basic/scenes/Main.json": json.dumps(
                {"name": "Main", "sources": [{"settings": {"file": original}}]}
            ),
            "media/0001_what?.png": "PNG",
        },
    )
    target, media_dir = tmp_path / "new", tmp_path / "m"
    sel = Selection(scene_collections=["Main.json"], media=True)
    backup.restore_backup(zip_path, target, sel, media_dir)
    assert _restored_paths(target) == [(media_dir / "what_.png").as_posix()]
    assert (media_dir / "what_.png").read_text() == "PNG"


# --- folders the user linked elsewhere -------------------------------------------------


def _link(link: Path, target: Path) -> None:
    """A symlink, or on Windows without the rights for one, a junction."""
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        if sys.platform != "win32":
            raise
        import _winapi

        _winapi.CreateJunction(str(target), str(link))


def _is_link(path: Path) -> bool:
    return path.is_symlink() or path.is_junction()


def test_restore_into_linked_scenes_folder(obs: Path, tmp_path: Path) -> None:
    synced = tmp_path / "synced scenes"
    shutil.move(obs / "basic/scenes", synced)
    _link(obs / "basic/scenes", synced)
    dest = tmp_path / "b.zip"
    sel = Selection(scene_collections=["Other.json"])
    backup.create_backup(obs, dest, sel)
    write(synced / "Other.json", "changed")

    backup.restore_backup(dest, obs, sel)
    assert _is_link(obs / "basic/scenes")
    assert json.loads((synced / "Other.json").read_text())["name"] == "Other"


def test_restore_into_linked_profile_folder(obs: Path, tmp_path: Path) -> None:
    synced = tmp_path / "synced profile"
    shutil.move(obs / "basic/profiles/Twitch_Stream", synced)
    _link(obs / "basic/profiles/Twitch_Stream", synced)
    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Twitch_Stream"])
    backup.create_backup(obs, dest, sel)
    write(synced / "stale.ini")

    backup.restore_backup(dest, obs, sel)
    assert _is_link(obs / "basic/profiles/Twitch_Stream")
    assert sorted(p.name for p in synced.iterdir()) == ["basic.ini", "service.json"]


# --- nothing changes when the backup turns out to be bad ------------------------------


def test_damaged_scene_collection_leaves_config_untouched(
    obs: Path, media: Path, tmp_path: Path
) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs))
    replace_member(dest, "config/basic/scenes/Main.json", "{not json")
    for f in media.iterdir():
        f.unlink()  # so the scene collection must be rewritten, which reads it
    write(obs / "basic/profiles/Twitch_Stream/added-later.ini")
    before = _files(obs)

    with pytest.raises(backup.InvalidBackupError):
        backup.restore_backup(dest, obs, everything(obs), tmp_path / "m")
    assert _files(obs) == before  # profile folder not deleted
    assert not (tmp_path / "m").exists()


def test_damaged_member_leaves_config_untouched(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Twitch_Stream"], global_settings=True)
    backup.create_backup(obs, dest, sel)
    corrupt_member(dest, "config/global.ini")  # after the profile in the backup
    write(obs / "basic/profiles/Twitch_Stream/added-later.ini")
    before = {f: (obs / f).read_bytes() for f in _files(obs)}

    with pytest.raises(backup.InvalidBackupError, match="global.ini"):
        backup.restore_backup(dest, obs, sel)
    assert {f: (obs / f).read_bytes() for f in _files(obs)} == before
    assert not list(obs.glob(".restore-*"))  # temporary folder removed

    with pytest.raises(backup.InvalidBackupError):
        backup.restore_backup(dest, tmp_path / "new", sel)
    assert not (tmp_path / "new").exists()  # not left behind, empty


def test_restore_leaves_no_temporary_folder(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs, media=False))
    backup.restore_backup(dest, obs, everything(obs, media=False))
    assert not list(obs.glob(".restore-*"))


def test_unsafe_member_leaves_profiles_untouched(obs: Path, tmp_path: Path) -> None:
    zip_path = craft_backup(
        tmp_path / "bad.zip",
        {"profiles": [{"name": "Twitch Stream", "dir": "Twitch_Stream"}]},
        {
            "config/basic/profiles/Twitch_Stream/basic.ini": "[General]\n",
            "config/plugin_manager/../../../evil.txt": "x",
        },
    )
    before = _files(obs)
    with pytest.raises(backup.InvalidBackupError):
        sel = Selection(profiles=["Twitch_Stream"], global_settings=True)
        backup.restore_backup(zip_path, obs, sel)
    assert _files(obs) == before


# --- media with the same file name ----------------------------------------------------


def _scene_using(cfg: Path, paths: list[Path]) -> None:
    sources = [{"id": "image_source", "settings": {"file": p.as_posix()}} for p in paths]
    write(cfg / "basic/scenes/Main.json", json.dumps({"name": "Main", "sources": sources}))


def _restored_paths(cfg: Path) -> list[str]:
    scene = json.loads((cfg / "basic/scenes/Main.json").read_text(encoding="utf-8"))
    return [s["settings"]["file"] for s in scene["sources"]]


def test_media_with_the_same_name_are_kept_apart(tmp_path: Path) -> None:
    a = write(tmp_path / "a" / "logo.png", "from folder a")
    b = write(tmp_path / "b" / "logo.png", "from folder b, longer")
    cfg = tmp_path / "obs-studio"
    _scene_using(cfg, [a, b])
    dest = tmp_path / "b.zip"
    sel = Selection(scene_collections=["Main.json"], media=True)
    backup.create_backup(cfg, dest, sel)
    a.unlink()
    b.unlink()

    target, media_dir = tmp_path / "new", tmp_path / "restored"
    result = backup.restore_backup(dest, target, sel, media_dir)

    paths = _restored_paths(target)
    assert result.media_restored == 2 and len(set(paths)) == 2
    assert [Path(p).read_text() for p in paths] == ["from folder a", "from folder b, longer"]


def test_existing_media_reused_only_with_the_same_contents(tmp_path: Path) -> None:
    logo = write(tmp_path / "src" / "logo.png", "AAAA")
    cfg = tmp_path / "obs-studio"
    _scene_using(cfg, [logo])
    dest = tmp_path / "b.zip"
    sel = Selection(scene_collections=["Main.json"], media=True)
    backup.create_backup(cfg, dest, sel)
    logo.unlink()

    # Same name and size, other contents: an unrelated file that must not be used.
    media_dir = tmp_path / "restored"
    write(media_dir / "logo.png", "BBBB")
    backup.restore_backup(dest, tmp_path / "new", sel, media_dir)
    assert _restored_paths(tmp_path / "new") == [(media_dir / "logo_2.png").as_posix()]
    assert (media_dir / "logo.png").read_text() == "BBBB"
    assert (media_dir / "logo_2.png").read_text() == "AAAA"

    # Restoring again reuses the copy restored the first time.
    result = backup.restore_backup(dest, tmp_path / "again", sel, media_dir)
    assert _restored_paths(tmp_path / "again") == [(media_dir / "logo_2.png").as_posix()]
    assert result.media_restored == 0  # nothing copied
    assert sorted(p.name for p in media_dir.iterdir()) == ["logo.png", "logo_2.png"]


# --- safety backup --------------------------------------------------------------------


def test_safety_backup_holds_browser_data_when_it_is_restored(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, everything(obs, media=False))
    safety_dir = tmp_path / "safety"

    sel = Selection(browser_data=True)
    result = backup.restore_with_safety_backup(dest, obs, sel, safety_dir=safety_dir)
    assert result.safety_backup is not None
    names = zipfile.ZipFile(result.safety_backup).namelist()
    assert "config/plugin_config/obs-browser/Cookies" in names
    assert "config/basic/scenes/Main.json" in names


def test_safety_selection_leaves_out_browser_data_not_restored(obs: Path) -> None:
    assert not backup.safety_selection(obs, Selection(scene_collections=["Main.json"])).browser_data
    assert backup.safety_selection(obs, Selection(browser_data=True)).browser_data


def test_failed_restore_names_the_safety_backup(obs: Path, tmp_path: Path) -> None:
    zip_path = tmp_path / "b.zip"
    backup.create_backup(obs, zip_path, Selection(global_settings=True))
    corrupt_member(zip_path, "config/global.ini")  # found while unpacking, after the checks
    with pytest.raises(backup.RestoreFailedError) as info:
        backup.restore_with_safety_backup(
            zip_path, obs, Selection(global_settings=True), safety_dir=tmp_path / "safety"
        )
    safety = info.value.safety_backup
    assert str(safety) in str(info.value)
    assert "config/global.ini" in zipfile.ZipFile(safety).namelist()


def test_unsafe_backup_makes_no_safety_backup(obs: Path, tmp_path: Path) -> None:
    zip_path = craft_backup(tmp_path / "bad.zip", {}, {"config/plugin_manager/../../x": "x"})
    with pytest.raises(backup.InvalidBackupError) as info:
        backup.restore_with_safety_backup(
            zip_path, obs, Selection(global_settings=True), safety_dir=tmp_path / "safety"
        )
    assert not isinstance(info.value, backup.RestoreFailedError)
    assert not (tmp_path / "safety").exists()


def test_failed_safety_backup_is_not_named(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, Selection(global_settings=True))
    not_a_folder = write(tmp_path / "file")
    with pytest.raises(OSError):  # not a RestoreFailedError naming a file that isn't there
        backup.restore_with_safety_backup(
            dest, obs, Selection(global_settings=True), safety_dir=not_a_folder
        )


def test_no_safety_backup_without_folder(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    backup.create_backup(obs, dest, Selection(global_settings=True))
    result = backup.restore_with_safety_backup(dest, obs, Selection(global_settings=True))
    assert result.safety_backup is None and result.files == 3


def test_incomplete_safety_backup_stops_the_restore(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(global_settings=True)
    backup.create_backup(obs, dest, sel)
    write(obs / "global.ini", "[General]\nchanged=1\n")
    before = {f: (obs / f).read_bytes() for f in _files(obs)}
    safety_dir = tmp_path / "safety"

    # user.ini would be replaced, but the safety backup can't hold it.
    with (
        unreadable(monkeypatch, "user.ini"),
        pytest.raises(backup.IncompleteSafetyBackupError) as info,
    ):
        backup.restore_with_safety_backup(dest, obs, sel, safety_dir=safety_dir)
    assert info.value.skipped == ["user.ini"]
    assert {f: (obs / f).read_bytes() for f in _files(obs)} == before
    assert list(safety_dir.iterdir()) == []  # the incomplete safety backup is removed


def test_unreadable_file_the_restore_leaves_alone_does_not_stop_it(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(global_settings=True)
    backup.create_backup(obs, dest, sel)
    with unreadable(monkeypatch, "service.json"):  # in a profile, which is not restored
        result = backup.restore_with_safety_backup(dest, obs, sel, safety_dir=tmp_path / "s")
    assert result.safety_backup is not None and result.safety_backup.is_file()


# --- parts of the config folder the backup holds only partly ----------------------------


def test_profile_backed_up_partly_keeps_the_missing_files(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Twitch_Stream"])
    with unreadable(monkeypatch, "service.json"):
        backup.create_backup(obs, dest, sel)
    profile = obs / "basic/profiles/Twitch_Stream"
    write(profile / "basic.ini", "[General]\nName=Changed\n")

    result = backup.restore_backup(dest, obs, sel)
    assert (profile / "service.json").read_text() == '{"settings": {"key": "secret"}}'
    assert "Twitch Stream" in (profile / "basic.ini").read_text()
    assert result.kept_current == ["basic/profiles/Twitch_Stream/service.json"]


def test_browser_data_replaces_files_written_since(obs: Path, tmp_path: Path) -> None:
    """Chromium's databases must not meet newer journal or log files."""
    dest = tmp_path / "b.zip"
    sel = Selection(browser_data=True)
    backup.create_backup(obs, dest, sel)
    browser = obs / "plugin_config/obs-browser"
    write(browser / "Cookies-journal", "journal of a newer database")
    write(browser / "Local Storage/leveldb/000009.log", "newer log")

    backup.restore_backup(dest, obs, sel)
    assert not (browser / "Cookies-journal").exists()
    assert not (browser / "Local Storage/leveldb/000009.log").exists()
    assert (browser / "Cookies").read_text() == "cookies"
    assert (browser / "Cache/data_0").exists()  # caches are not in backups and stay


def test_browser_data_backed_up_partly_is_restored_over_current(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    browser = obs / "plugin_config/obs-browser"
    write(browser / "Preferences", "old prefs")
    dest = tmp_path / "b.zip"
    sel = Selection(browser_data=True)
    with unreadable(monkeypatch, "Cookies"):
        backup.create_backup(obs, dest, sel)
    write(browser / "Cookies", "newer cookies")
    write(browser / "Preferences", "newer prefs")

    result = backup.restore_backup(dest, obs, sel)
    assert (browser / "Preferences").read_text() == "old prefs"
    assert (browser / "Cookies").read_text() == "newer cookies"  # not in the backup: kept
    assert result.kept_current == ["plugin_config/obs-browser/Cookies"]


# --- something on disk in the way ---------------------------------------------------------


def test_folder_in_the_way_stops_before_any_change(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(scene_collections=["Other.json"], global_settings=True)
    backup.create_backup(obs, dest, sel)
    (obs / "basic/scenes/Other.json").unlink()
    (obs / "basic/scenes/Other.json").mkdir()
    write(obs / "global.ini", "changed")

    with pytest.raises(backup.BackupError, match="in the way"):
        backup.restore_backup(dest, obs, sel)
    assert (obs / "global.ini").read_text() == "changed"


def test_file_in_the_way_of_a_folder_stops_before_any_change(obs: Path, tmp_path: Path) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(global_settings=True)  # holds plugin_manager/modules.json
    backup.create_backup(obs, dest, sel)
    shutil.rmtree(obs / "plugin_manager")
    write(obs / "plugin_manager", "a file, not a folder")
    write(obs / "global.ini", "changed")

    with pytest.raises(backup.BackupError, match="not a folder"):
        backup.restore_backup(dest, obs, sel)
    assert (obs / "global.ini").read_text() == "changed"


def test_file_where_an_emptied_profile_folder_goes_stops_before_any_change(
    obs: Path, tmp_path: Path
) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Unbenannt"], global_settings=True)
    backup.create_backup(obs, dest, sel)
    shutil.rmtree(obs / "basic/profiles/Unbenannt")
    write(obs / "basic/profiles/Unbenannt", "a file, not a folder")
    write(obs / "global.ini", "changed")

    with pytest.raises(backup.BackupError, match="not a folder"):
        backup.restore_backup(dest, obs, sel)
    assert (obs / "global.ini").read_text() == "changed"


def _replace_failing_from_staging(monkeypatch: pytest.MonkeyPatch, error: OSError) -> None:
    """``os.replace`` fails for files unpacked to the restore's temporary folder."""
    real_replace = os.replace

    def replace(src: Any, dst: Any) -> None:
        if Path(src).parent.name.startswith(".restore-"):
            raise error
        real_replace(src, dst)

    monkeypatch.setattr(os, "replace", replace)


def test_restore_onto_another_drive_copies(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(global_settings=True)
    backup.create_backup(obs, dest, sel)
    write(obs / "global.ini", "changed")
    _replace_failing_from_staging(monkeypatch, OSError(errno.EXDEV, "another drive"))

    backup.restore_backup(dest, obs, sel)
    assert "Language=de-DE" in (obs / "global.ini").read_text()
    assert not list(obs.rglob("*.restore-tmp"))


def test_other_errors_moving_a_file_are_not_hidden(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "b.zip"
    sel = Selection(global_settings=True)
    backup.create_backup(obs, dest, sel)
    _replace_failing_from_staging(monkeypatch, PermissionError(errno.EACCES, "denied"))
    with pytest.raises(PermissionError):
        backup.restore_backup(dest, obs, sel)


@pytest.mark.usefixtures("on_windows")
def test_files_of_a_linux_profile_with_backslash_stay_out_of_other_profiles(
    tmp_path: Path,
) -> None:
    """On Windows, zipfile reads "a\\b/basic.ini" as "a/b/basic.ini": a file of "a"."""
    zip_path = craft_backup(
        tmp_path / "linux.zip",
        {"profiles": [{"dir": "a"}, {"dir": r"a\b"}], "skipped": []},
        {
            "config/basic/profiles/a/basic.ini": "[General]\nName=a\n",
            "config/basic/profiles/a\\b/basic.ini": "[General]\nName=a and b\n",
        },
    )
    target = tmp_path / "new"
    backup.restore_backup(zip_path, target, Selection(profiles=["a"]))
    assert _files(target) == ["basic/profiles/a/basic.ini"]


def test_name_holding_nul_is_refused(tmp_path: Path) -> None:
    """zipfile cuts such a name short, which would restore "a" for "a\\0../../evil"."""
    zip_path = craft_backup(tmp_path / "bad.zip", {}, {"config/plugin_manager/a\0evil": "x"})
    with pytest.raises(backup.InvalidBackupError, match="Unsafe path"):
        backup.restore_backup(zip_path, tmp_path / "cfg", Selection(global_settings=True))
    assert not (tmp_path / "cfg").exists()


def test_backup_from_an_older_version_removes_no_files(obs: Path, tmp_path: Path) -> None:
    """Older backups don't record which files they lack, so none count as complete."""
    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Twitch_Stream"], browser_data=True)
    backup.create_backup(obs, dest, sel)
    with zipfile.ZipFile(dest) as zf:
        manifest = json.loads(zf.read("manifest.json"))
    del manifest["skipped"]
    replace_member(dest, "manifest.json", json.dumps(manifest))
    assert backup.read_manifest(dest).skipped is None
    write(obs / "basic/profiles/Twitch_Stream/added-later.ini")
    write(obs / "plugin_config/obs-browser/Preferences", "newer")

    backup.restore_backup(dest, obs, sel)
    assert (obs / "basic/profiles/Twitch_Stream/added-later.ini").exists()
    assert (obs / "plugin_config/obs-browser/Preferences").exists()
    assert "Twitch Stream" in (obs / "basic/profiles/Twitch_Stream/basic.ini").read_text()


def test_profile_with_a_folder_that_could_not_be_listed_keeps_it(
    obs: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    extra = write(obs / "basic/profiles/Twitch_Stream/sub/extra.ini")
    real_scandir = os.scandir

    def scandir(path: Any = ".") -> Any:
        if Path(path).name == "sub":
            raise PermissionError(13, "Access is denied", str(path))
        return real_scandir(path)

    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Twitch_Stream"])
    with monkeypatch.context() as m:
        m.setattr(os, "scandir", scandir)
        backup.create_backup(obs, dest, sel)
    result = backup.restore_backup(dest, obs, sel)
    assert extra.exists()
    assert result.kept_current == ["basic/profiles/Twitch_Stream/sub/"]


def test_linked_folder_inside_a_profile_survives_the_restore(obs: Path, tmp_path: Path) -> None:
    elsewhere = tmp_path / "overlays"
    write(elsewhere / "overlay.png", "PNG")
    _link(obs / "basic/profiles/Twitch_Stream/overlays", elsewhere)
    dest = tmp_path / "b.zip"
    sel = Selection(profiles=["Twitch_Stream"])
    backup.create_backup(obs, dest, sel)

    backup.restore_backup(dest, obs, sel)
    assert _is_link(obs / "basic/profiles/Twitch_Stream/overlays")
    assert (elsewhere / "overlay.png").read_text() == "PNG"
