"""Layout of a backup file.

A backup is a plain zip file::

    manifest.json          what the backup holds (see ``manifest.Manifest``)
    config/...             files from the OBS config folder, same relative layout
    media/0001_logo.png    optional copies of media files the scene collections use
"""

import ntpath
import re
import sys
from pathlib import Path

WINDOWS = sys.platform == "win32"

FORMAT = "obs-backup"
FORMAT_VERSION = 1

MANIFEST = "manifest.json"
CONFIG_PREFIX = "config/"
MEDIA_PREFIX = "media/"


def is_plain_name(name: str) -> bool:
    """Whether ``name`` is one file or folder name on this OS, safe to join to a folder.

    Profile folders, scene collection files and media file names come from the
    backup's manifest, so they must not be able to point anywhere else
    (``..``, ``a/b``, or ``C:x`` on Windows).
    """
    if name in ("", ".", "..") or any(c in name for c in "/\\\0"):
        return False
    path = Path(name)
    return len(path.parts) == 1 and path.name == name


def can_create(rel: str) -> bool:
    """Whether this OS allows every name in ``rel`` (a ``/``-separated path).

    A backup from Linux or macOS can hold names Windows refuses: ``a?b``, ``x:y``,
    a trailing dot, or device names such as ``CON``. Checking them first keeps a
    restore from failing halfway.
    """
    return not (WINDOWS and ntpath.isreserved(rel))


_NOT_ON_WINDOWS = re.compile(r'[<>:"|?*\x00-\x1f]')


def creatable_name(name: str) -> str:
    """``name``, changed where needed so that this OS can create a file with it."""
    if can_create(name):
        return name
    name = _NOT_ON_WINDOWS.sub("_", name).rstrip(" .") or "_"
    return name if can_create(name) else f"_{name}"  # a device name such as CON.png
