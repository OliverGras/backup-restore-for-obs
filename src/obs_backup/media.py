"""Find and rewrite the local file paths that scene collections refer to.

Sources such as images, media, slideshows, browser sources with a local file,
or text sources reading from a file store absolute paths in the scene
collection JSON. OBS writes them with forward slashes, also on Windows
(``C:/Users/me/Videos/intro.mp4``).
"""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Callable, Iterator

_WIN_ABS = re.compile(r"^[A-Za-z]:[\\/]")


def looks_like_local_path(value: str) -> bool:
    if not value or len(value) > 1024 or "\n" in value:
        return False
    if "://" in value:
        return False
    return bool(_WIN_ABS.match(value)) or value.startswith(("/", "\\\\"))


def file_name(path: str) -> str:
    """File name of a path that may come from another OS."""
    if _WIN_ABS.match(path) or "\\" in path:
        return PureWindowsPath(path).name
    return PurePosixPath(path).name


def iter_strings(obj: Any) -> Iterator[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)


def replace_strings(obj: Any, fn: Callable[[str], str]) -> Any:
    if isinstance(obj, str):
        return fn(obj)
    if isinstance(obj, dict):
        return {k: replace_strings(v, fn) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_strings(v, fn) for v in obj]
    return obj


def find_media_files(scene_json: Any) -> list[str]:
    """Absolute paths of existing files referenced by a scene collection, as stored."""
    seen: dict[str, None] = {}
    for s in iter_strings(scene_json):
        if s in seen or not looks_like_local_path(s):
            continue
        try:
            if Path(s).is_file():
                seen[s] = None
        except (OSError, ValueError):
            continue
    return list(seen)


def load_scene_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def rewrite_paths(scene_json: Any, mapping: dict[str, str]) -> Any:
    if not mapping:
        return scene_json
    return replace_strings(scene_json, lambda s: mapping.get(s, s))


def dump_scene_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=4)
