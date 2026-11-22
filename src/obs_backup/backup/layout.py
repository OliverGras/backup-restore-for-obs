"""Layout of a backup file.

A backup is a plain zip file::

    manifest.json          what the backup holds (see ``manifest.Manifest``)
    config/...             files from the OBS config folder, same relative layout
    media/0001_logo.png    optional copies of media files the scene collections use
"""

FORMAT = "obs-backup"
FORMAT_VERSION = 1

MANIFEST = "manifest.json"
CONFIG_PREFIX = "config/"
MEDIA_PREFIX = "media/"
