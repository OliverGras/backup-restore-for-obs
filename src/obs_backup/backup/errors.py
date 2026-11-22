"""Errors raised while creating or restoring backups."""

import zipfile
import zlib
from pathlib import Path

# Raised while reading a zip member that is damaged (bad data or CRC, truncated),
# uses unsupported compression, or is encrypted (RuntimeError).
ZIP_ERRORS = (zipfile.BadZipFile, zlib.error, EOFError, NotImplementedError, RuntimeError)


class BackupError(Exception):
    """A backup could not be created or restored."""


class InvalidBackupError(BackupError):
    """A file is not a valid backup, or is damaged or unsafe."""


class RestoreFailedError(BackupError):
    """A restore failed; ``safety_backup`` holds the config folder as it was before."""

    def __init__(self, error: BaseException, safety_backup: Path) -> None:
        self.reason = str(error) or type(error).__name__
        self.safety_backup = safety_backup
        super().__init__(
            f"{self.reason}\n\nThe OBS config folder as it was before the restore is saved in "
            f"{safety_backup}"
        )


class IncompleteSafetyBackupError(BackupError):
    """The safety backup could not read every file, so the restore did not start.

    Nothing was changed. ``skipped`` lists the files (relative to the config folder).
    """

    def __init__(self, skipped: list[str]) -> None:
        self.skipped = skipped
        super().__init__(
            f"the current state could not be backed up completely, so nothing was "
            f"restored; {len(skipped)} files could not be read: {', '.join(skipped[:10])}"
        )
