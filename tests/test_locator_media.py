from pathlib import Path

from obs_backup import locator
from obs_backup.i18n import STRINGS, system_language
from obs_backup.media import file_name, find_media_files, looks_like_local_path


def test_default_dirs() -> None:
    home = Path("/home/me")
    assert locator.default_config_dir("win32", {"APPDATA": r"C:\Users\me\AppData\Roaming"}, home) == \
        Path(r"C:\Users\me\AppData\Roaming") / "obs-studio"
    assert locator.default_config_dir("darwin", {}, home) == home / "Library/Application Support/obs-studio"
    assert locator.default_config_dir("linux", {}, home) == home / ".config/obs-studio"
    assert locator.default_config_dir("linux", {"XDG_CONFIG_HOME": "/xdg"}, home) == Path("/xdg/obs-studio")


def test_portable_by_marker_file(tmp_path: Path) -> None:
    exe = tmp_path / "OBS" / "bin" / "64bit" / "obs64.exe"
    exe.parent.mkdir(parents=True)
    exe.touch()
    cfg, kind = locator.config_dir_for_process(exe, [str(exe)], "win32", {"APPDATA": "C:/AD"})
    assert kind == "standard" and cfg == Path("C:/AD/obs-studio")

    (tmp_path / "OBS" / "obs_portable_mode.txt").touch()
    cfg, kind = locator.config_dir_for_process(exe, [str(exe)], "win32", {"APPDATA": "C:/AD"})
    assert kind == "portable" and cfg == tmp_path / "OBS" / "config" / "obs-studio"


def test_portable_by_flag(tmp_path: Path) -> None:
    exe = tmp_path / "OBS" / "bin" / "64bit" / "obs64.exe"
    cfg, kind = locator.config_dir_for_process(exe, [str(exe), "--portable"], "win32", {})
    assert kind == "portable" and cfg == tmp_path / "OBS" / "config" / "obs-studio"


def test_linux_sandboxes() -> None:
    home = Path("/home/me")
    cfg, kind = locator.config_dir_for_process(Path("/app/bin/obs"), ["obs"], "linux", {}, home)
    assert kind == "flatpak" and cfg == home / ".var/app/com.obsproject.Studio/config/obs-studio"
    cfg, kind = locator.config_dir_for_process(Path("/snap/obs-studio/1234/usr/bin/obs"), ["obs"], "linux", {}, home)
    assert kind == "snap" and cfg == home / "snap/obs-studio/current/.config/obs-studio"


def test_discover_always_returns_something() -> None:
    assert locator.discover()


def test_path_heuristic() -> None:
    assert looks_like_local_path("C:/Users/me/a.png")
    assert looks_like_local_path(r"D:\clips\b.mp4")
    assert looks_like_local_path("/home/me/a.png")
    assert looks_like_local_path(r"\\nas\share\c.mp3")
    assert not looks_like_local_path("https://example.com/a.png")
    assert not looks_like_local_path("file:///C:/a.png")
    assert not looks_like_local_path("relative/a.png")
    assert not looks_like_local_path("")


def test_find_media_only_existing(tmp_path: Path) -> None:
    f = tmp_path / "a.png"
    f.write_text("x")
    data = {"a": f.as_posix(), "b": [{"value": f.as_posix()}], "c": (tmp_path / "missing.png").as_posix()}
    assert find_media_files(data) == [f.as_posix()]


def test_file_name_cross_os() -> None:
    assert file_name("C:/Users/me/logo.png") == "logo.png"
    assert file_name(r"C:\Users\me\logo.png") == "logo.png"
    assert file_name("/home/me/logo.png") == "logo.png"


def test_translations_complete() -> None:
    assert set(STRINGS["de"]) == set(STRINGS["en"])
    assert system_language("de_DE") == "de"
    assert system_language("en_US") == "en"
    assert system_language("fr_FR") == "en"


def test_license_texts_present() -> None:
    from obs_backup.legal import license_documents

    names = [name for name, _ in license_documents()]
    for required in ("LICENSE", "THIRD_PARTY_NOTICES.md", "LGPL-3.0.txt", "GPL-3.0.txt",
                     "psutil-BSD-3-Clause.txt", "Python-PSF.txt",
                     "PyInstaller-GPL-2.0-with-exception.txt"):
        assert required in names
