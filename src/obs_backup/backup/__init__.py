"""Backup files: what goes into them, creating them and restoring them.

- ``layout``:   how a backup zip is organised
- ``models``:   ``Selection`` (what to back up or restore) and result types
- ``manifest``: the manifest.json inside every backup; finding backups
- ``collect``:  which files and media a selection covers
- ``create``:   writing a backup
- ``restore``:  restoring a backup
"""

from obs_backup.backup.collect import collect_files, full_selection, safety_selection, scan_media
from obs_backup.backup.create import create_backup, default_backup_name, new_backup_path
from obs_backup.backup.errors import (
    BackupError,
    IncompleteSafetyBackupError,
    InvalidBackupError,
    RestoreFailedError,
)
from obs_backup.backup.manifest import (
    Manifest,
    ProfileEntry,
    SceneCollectionEntry,
    list_backups,
    read_manifest,
)
from obs_backup.backup.models import BackupResult, MediaRef, Progress, RestoreResult, Selection
from obs_backup.backup.restore import restore_backup, restore_with_safety_backup

__all__ = [
    "BackupError",
    "BackupResult",
    "IncompleteSafetyBackupError",
    "InvalidBackupError",
    "Manifest",
    "MediaRef",
    "ProfileEntry",
    "Progress",
    "RestoreFailedError",
    "RestoreResult",
    "SceneCollectionEntry",
    "Selection",
    "collect_files",
    "create_backup",
    "default_backup_name",
    "full_selection",
    "list_backups",
    "new_backup_path",
    "read_manifest",
    "restore_backup",
    "restore_with_safety_backup",
    "safety_selection",
    "scan_media",
]
