"""Read the contents of an OBS configuration folder.

Layout (OBS 28+, still current in OBS 33)::

    obs-studio/
      global.ini, user.ini        general settings (user.ini since OBS 31)
      plugin_manager/             enabled / disabled plugins (OBS 32+)
      basic/profiles/<dir>/       one folder per profile (basic.ini, service.json, ...)
      basic/scenes/<name>.json    one file per scene collection, holding scenes and sources
      plugin_config/<plugin>/     plugin settings (obs-websocket, ...)
      plugin_config/obs-browser/  Chromium data of browser sources and docks: cache, cookies, logins
      plugins/                    user-installed plugins (macOS / Linux)
      logs/, crashes/, ...        not backed up
"""

import configparser
import contextlib
import json
import re
from dataclasses import dataclass
from itertools import islice
from pathlib import Path

PROFILES_DIR = Path("basic") / "profiles"
SCENES_DIR = Path("basic") / "scenes"
GLOBAL_FILES = ("global.ini", "user.ini")
GLOBAL_DIRS = ("plugin_manager",)
PLUGIN_CONFIG_DIR = Path("plugin_config")
BROWSER_DIR = PLUGIN_CONFIG_DIR / "obs-browser"
PLUGINS_DIR = Path("plugins")

# Chromium folders inside obs-browser that only hold caches or components Chromium
# downloads again by itself. Cookies, Local Storage and IndexedDB (logins) are kept.
BROWSER_CACHE_DIRS = frozenset(
    {
        # caches
        "cache",
        "code cache",
        "gpucache",
        "dawncache",
        "dawngraphitecache",
        "dawnwebgpucache",
        "grshadercache",
        "graphitedawncache",
        "shadercache",
        "crashpad",
        "blob_storage",
        "component_crx_cache",
        "optimization_guide_model_store",
        # components from the Chromium component updater
        "widevinecdm",
        "wasmttsengine",
        "certificaterevocation",
        "ondeviceheadsuggestmodel",
        "dictionaries",
        "optimizationhints",
        "safe browsing",
        "hyphen-data",
        "meipreload",
        "pkimetadata",
        "safetytips",
        "filetypepolicies",
        "origintrials",
        "segmentation_platform",
        "crowd deny",
        "actorsafetylists",
        "amountextractionheuristicregexes",
        "captchaproviders",
        "firstpartysetspreloaded",
        "privacysandboxattestationspreloaded",
        "zxcvbndata",
        "trusttokenkeycommitments",
        "sslerrorassistant",
        "subresource filter",
        "autofillstates",
        "screen_ai",
        "probabilisticrevealtokenregistry",
        "cookiereadinesslist",
    }
)
# Lock files Chromium keeps open while OBS runs.
BROWSER_SKIP_FILES = frozenset({"lock", "lockfile", "singletonlock"})

_VERSION_RE = re.compile(r"\bOBS (\d+\.\d+(?:\.\d+)?\S*) \(")


@dataclass(frozen=True)
class Profile:
    name: str
    dir_name: str


@dataclass(frozen=True)
class SceneCollection:
    name: str
    file_name: str


class _CaseKeepingParser(configparser.ConfigParser):
    """ConfigParser that keeps the case of keys (OBS writes keys like ``ProfileDir``)."""

    def optionxform(self, optionstr: str) -> str:
        return optionstr


def read_ini(path: Path) -> configparser.ConfigParser:
    parser = _CaseKeepingParser(interpolation=None, strict=False)
    with contextlib.suppress(OSError, configparser.Error):
        parser.read_string(path.read_text(encoding="utf-8-sig", errors="replace"))
    return parser


def list_profiles(config_dir: Path) -> list[Profile]:
    root = config_dir / PROFILES_DIR
    if not root.is_dir():
        return []
    profiles = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        ini = read_ini(d / "basic.ini")
        name = ini.get("General", "Name", fallback=d.name) or d.name
        profiles.append(Profile(name=name, dir_name=d.name))
    return profiles


# Encoders that need particular graphics hardware, matched by part of the encoder id
# a profile stores (OBS has used several ids per vendor: "nvenc", "jim_nvenc",
# "obs_nvenc_av1_tex", "ffmpeg_nvenc", "h264_texture_amf", "obs_qsv11", ...).
HARDWARE_ENCODERS = (
    ("nvenc", "NVIDIA NVENC"),
    ("amf", "AMD AMF"),
    ("amd", "AMD AMF"),
    ("qsv", "Intel Quick Sync"),
    ("vaapi", "VA-API"),
    ("apple", "Apple VideoToolbox"),
)


def _hardware_vendor(encoder: str) -> str | None:
    encoder = encoder.lower()
    return next((vendor for part, vendor in HARDWARE_ENCODERS if part in encoder), None)


def profile_encoders(profile_dir: Path) -> list[str]:
    """The encoder ids a profile uses for streaming and recording, from its basic.ini.

    Only the encoders of the output mode the profile is set to; a recording that
    uses the stream encoder adds none of its own. Encoders not set are left out:
    OBS then picks one itself.
    """
    ini = read_ini(profile_dir / "basic.ini")
    if ini.get("Output", "Mode", fallback="Simple") == "Advanced":
        ids = [ini.get("AdvOut", "Encoder", fallback="")]
        if ini.get("AdvOut", "RecType", fallback="Standard") == "Standard":
            ids.append(ini.get("AdvOut", "RecEncoder", fallback="none"))
    else:
        ids = [ini.get("SimpleOutput", "StreamEncoder", fallback="")]
        if ini.get("SimpleOutput", "RecQuality", fallback="Stream") != "Stream":
            ids.append(ini.get("SimpleOutput", "RecEncoder", fallback=""))
    return [i for i in ids if i and i != "none"]


def hardware_encoders(profile_dir: Path) -> list[str]:
    """The kinds of hardware encoder a profile uses, e.g. ``["NVIDIA NVENC"]``.

    These only work on a computer with that graphics hardware and its driver.
    """
    vendors = (_hardware_vendor(e) for e in profile_encoders(profile_dir))
    return list(dict.fromkeys(v for v in vendors if v))


def scene_collection_name(path: Path) -> str:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        name = data.get("name") if isinstance(data, dict) else None
        if isinstance(name, str) and name:
            return name
    except OSError, ValueError:
        pass
    return path.stem


def list_scene_collections(config_dir: Path) -> list[SceneCollection]:
    root = config_dir / SCENES_DIR
    if not root.is_dir():
        return []
    return [
        SceneCollection(name=scene_collection_name(f), file_name=f.name)
        for f in sorted(root.glob("*.json"))
        if f.is_file()
    ]


def has_global_settings(config_dir: Path) -> bool:
    return any((config_dir / f).is_file() for f in GLOBAL_FILES) or any(
        (config_dir / d).is_dir() for d in GLOBAL_DIRS
    )


def has_plugin_config(config_dir: Path) -> bool:
    root = config_dir / PLUGIN_CONFIG_DIR
    return root.is_dir() and any(p.name != BROWSER_DIR.name for p in root.iterdir())


def has_browser_data(config_dir: Path) -> bool:
    return (config_dir / BROWSER_DIR).is_dir()


def has_plugins(config_dir: Path) -> bool:
    root = config_dir / PLUGINS_DIR
    return root.is_dir() and any(root.iterdir())


def _mtime(path: Path) -> float:
    """Modification time, or 0 for a file that vanished (OBS removes old logs)."""
    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0


def obs_version(config_dir: Path) -> str | None:
    """The OBS version from the newest log file, e.g. ``"33.0.1"``."""
    logs = config_dir / "logs"
    if not logs.is_dir():
        return None
    files = sorted((f for f in logs.glob("*.txt") if f.is_file()), key=_mtime, reverse=True)
    for f in files[:3]:
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                for line in islice(fh, 80):
                    m = _VERSION_RE.search(line)
                    if m:
                        return m.group(1)
        except OSError:
            continue
    return None
