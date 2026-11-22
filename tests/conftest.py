"""Test data: a fake OBS config folder with profiles, scene collections and media."""

import json
import os
from pathlib import Path

import pytest

from support import write

# GUI tests run without a screen.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture
def media(tmp_path: Path) -> Path:
    d = tmp_path / "media"
    write(d / "logo.png", "PNG")
    write(d / "intro.mp4", "MP4" * 100)
    return d


@pytest.fixture
def obs(tmp_path: Path, media: Path) -> Path:
    """An OBS config folder like a real one, small enough for tests."""
    cfg = tmp_path / "obs-studio"
    write(cfg / "global.ini", "[General]\nLanguage=de-DE\n")
    write(cfg / "user.ini", "[Basic]\nProfile=Stream\n")
    write(cfg / "plugin_manager" / "modules.json", "{}")
    write(cfg / "basic/profiles/Twitch_Stream/basic.ini", "[General]\nName=Twitch Stream\n")
    write(cfg / "basic/profiles/Twitch_Stream/service.json", '{"settings": {"key": "secret"}}')
    write(cfg / "basic/profiles/Unbenannt/basic.ini", "[General]\nName=Unbenannt\n")
    logo, intro = (media / "logo.png").as_posix(), (media / "intro.mp4").as_posix()
    scene = {
        "name": "Main Scenes",
        "sources": [
            {"id": "image_source", "settings": {"file": logo}},
            {"id": "ffmpeg_source", "settings": {"local_file": intro}},
            {"id": "slideshow", "settings": {"files": [{"value": logo}]}},
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
