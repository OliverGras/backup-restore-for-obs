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


def read_ini(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.optionxform = str  # keep key case
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


def has_plugin_config(config_dir: Path) -> bool:
    root = config_dir / PLUGIN_CONFIG_DIR
    return root.is_dir() and any(p.name != BROWSER_DIR.name for p in root.iterdir())


def has_browser_data(config_dir: Path) -> bool:
    return (config_dir / BROWSER_DIR).is_dir()


def has_plugins(config_dir: Path) -> bool:
    root = config_dir / PLUGINS_DIR
    return root.is_dir() and any(root.iterdir())


def obs_version(config_dir: Path) -> str | None:
    """The OBS version from the newest log file, e.g. ``"33.0.1"``."""
    logs = config_dir / "logs"
    if not logs.is_dir():
        return None
    files = sorted(
        (f for f in logs.glob("*.txt") if f.is_file()),
        key=lambda f: f.stat().st_mtime,
        reverse=True,
    )
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
