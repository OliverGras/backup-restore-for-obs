"""Find OBS Studio installations and their configuration folders.

Where OBS keeps its configuration:

* Windows:        ``%APPDATA%\\obs-studio``
* macOS:          ``~/Library/Application Support/obs-studio``
* Linux:          ``$XDG_CONFIG_HOME/obs-studio`` (default ``~/.config/obs-studio``)
* Linux Flatpak:  ``~/.var/app/com.obsproject.Studio/config/obs-studio``
* Linux Snap:     ``~/snap/obs-studio/current/.config/obs-studio``
* Portable mode:  ``<install root>/config/obs-studio``. Portable mode is on when the
  install root holds ``obs_portable_mode.txt`` / ``portable_mode.txt`` or OBS was
  started with ``--portable`` / ``-p``.

A running OBS process is used to find its executable, and from that whether it runs
in portable mode.
"""

import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import psutil

PROCESS_NAMES = {"obs64.exe", "obs32.exe", "obs.exe", "obs"}
PORTABLE_MARKERS = (
    "obs_portable_mode.txt",
    "portable_mode.txt",
    "obs_portable_mode",
    "portable_mode",
)
PORTABLE_FLAGS = {"--portable", "-p"}
FLATPAK_ID = "com.obsproject.Studio"


@dataclass
class RunningObs:
    pid: int
    executable: Path | None
    cmdline: list[str] = field(default_factory=list)


@dataclass
class ObsInstallation:
    config_dir: Path
    kind: str  # "standard", "portable", "flatpak", "snap", "custom"
    executable: Path | None = None
    running: bool = False

    @property
    def exists(self) -> bool:
        return self.config_dir.is_dir()


def _home() -> Path:
    return Path.home()


def default_config_dir(
    platform: str | None = None, env: Mapping[str, str] | None = None, home: Path | None = None
) -> Path:
    platform = platform or sys.platform
    environ: Mapping[str, str] = os.environ if env is None else env
    home = home or _home()
    if platform.startswith("win"):
        appdata = environ.get("APPDATA") or str(home / "AppData" / "Roaming")
        return Path(appdata) / "obs-studio"
    if platform == "darwin":
        return home / "Library" / "Application Support" / "obs-studio"
    xdg = environ.get("XDG_CONFIG_HOME") or str(home / ".config")
    return Path(xdg) / "obs-studio"


def flatpak_config_dir(home: Path | None = None) -> Path:
    return (home or _home()) / ".var" / "app" / FLATPAK_ID / "config" / "obs-studio"


def snap_config_dir(home: Path | None = None) -> Path:
    return (home or _home()) / "snap" / "obs-studio" / "current" / ".config" / "obs-studio"


def install_root(executable: Path) -> Path:
    """The OBS install root for an executable at ``<root>/bin/64bit/obs64.exe``."""
    parents = executable.parents
    return parents[2] if len(parents) > 2 else executable.parent


def is_portable(executable: Path | None, cmdline: list[str]) -> bool:
    if any(arg in PORTABLE_FLAGS for arg in cmdline[1:]):
        return True
    if executable is None:
        return False
    root = install_root(executable)
    return any((root / marker).exists() for marker in PORTABLE_MARKERS)


def config_dir_for_process(
    executable: Path | None,
    cmdline: list[str],
    platform: str | None = None,
    env: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> tuple[Path, str]:
    """Work out which configuration folder a running OBS process uses."""
    platform = platform or sys.platform
    if executable is not None:
        exe = executable.as_posix()
        if platform.startswith("linux"):
            if exe.startswith("/app/"):
                return flatpak_config_dir(home), "flatpak"
            if exe.startswith("/snap/"):
                return snap_config_dir(home), "snap"
    if executable is not None and is_portable(executable, cmdline):
        return install_root(executable) / "config" / "obs-studio", "portable"
    return default_config_dir(platform, env, home), "standard"


def find_running_obs() -> list[RunningObs]:
    found: list[RunningObs] = []
    for proc in psutil.process_iter(["name"]):
        try:
            if (proc.info.get("name") or "").lower() not in PROCESS_NAMES:
                continue
            # Only for OBS: reading these for every process is slow, and this runs
            # every few seconds. None where access is denied.
            info = proc.as_dict(["exe", "cmdline"], ad_value=None)
            exe = info["exe"]
            found.append(
                RunningObs(
                    pid=proc.pid,
                    executable=Path(exe) if exe else None,
                    cmdline=list(info["cmdline"] or []),
                )
            )
        except psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess:
            continue
    return found


def _same(a: Path, b: Path) -> bool:
    try:
        return os.path.normcase(a.resolve()) == os.path.normcase(b.resolve())
    except OSError:
        return os.path.normcase(str(a)) == os.path.normcase(str(b))


def discover() -> list[ObsInstallation]:
    """All OBS configuration folders found on this machine, running instances first."""
    result: list[ObsInstallation] = []

    def add(inst: ObsInstallation) -> None:
        for existing in result:
            if _same(existing.config_dir, inst.config_dir):
                existing.running = existing.running or inst.running
                existing.executable = existing.executable or inst.executable
                return
        result.append(inst)

    for proc in find_running_obs():
        cfg, kind = config_dir_for_process(proc.executable, proc.cmdline)
        add(ObsInstallation(cfg, kind, proc.executable, running=True))

    candidates = [(default_config_dir(), "standard")]
    if sys.platform.startswith("linux"):
        candidates += [(flatpak_config_dir(), "flatpak"), (snap_config_dir(), "snap")]
    for cfg, kind in candidates:
        if cfg.is_dir():
            add(ObsInstallation(cfg, kind))

    if not result:
        # Nothing found: still offer the default location so a backup can be restored
        # onto a machine where OBS has never been started.
        result.append(ObsInstallation(default_config_dir(), "standard"))
    return result


def running_obs_for(config_dir: Path) -> RunningObs | None:
    """The running OBS process that uses ``config_dir``, if any.

    A process whose executable cannot be read (access denied) counts as a match,
    so the caller errs on the side of caution.
    """
    for proc in find_running_obs():
        if proc.executable is None:
            return proc
        cfg, _ = config_dir_for_process(proc.executable, proc.cmdline)
        if _same(cfg, config_dir):
            return proc
    return None
