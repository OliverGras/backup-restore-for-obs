"""Layout of a backup file.

A backup is a plain zip file::

    manifest.json          what the backup holds (see ``manifest.Manifest``)
    config/...             files from the OBS config folder, same relative layout
    media/0001_logo.png    optional copies of media files the scene collections use
"""

from pathlib import Path

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
