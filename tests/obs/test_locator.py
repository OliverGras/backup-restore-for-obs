"""Finding OBS and its config folder."""

from pathlib import Path

from obs_backup.obs import locator


def test_default_dirs() -> None:
    home = Path("/home/me")
    assert (
        locator.default_config_dir("win32", {"APPDATA": r"C:\Users\me\AppData\Roaming"}, home)
        == Path(r"C:\Users\me\AppData\Roaming") / "obs-studio"
    )
    assert (
        locator.default_config_dir("darwin", {}, home)
        == home / "Library/Application Support/obs-studio"
    )
    assert locator.default_config_dir("linux", {}, home) == home / ".config/obs-studio"
    assert locator.default_config_dir("linux", {"XDG_CONFIG_HOME": "/xdg"}, home) == Path(
        "/xdg/obs-studio"
    )


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
    cfg, kind = locator.config_dir_for_process(
        Path("/snap/obs-studio/1234/usr/bin/obs"), ["obs"], "linux", {}, home
    )
    assert kind == "snap" and cfg == home / "snap/obs-studio/current/.config/obs-studio"


def test_discover_always_returns_something() -> None:
    assert locator.discover()
