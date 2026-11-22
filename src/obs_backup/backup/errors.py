"""Errors raised while creating or restoring backups.

Each error names its message with a ``code``: the UI text ``error_<code>``, filled
in with ``params``. ``str()`` gives the message in English; the user interface
words it in the user's language (``gui.helpers.error_message``).
"""

import zipfile
import zlib
from pathlib import Path

from obs_backup.i18n import en, preview_list

# Raised while reading a zip member that is damaged (bad data or CRC, truncated),
# uses unsupported compression, or is encrypted (RuntimeError).
ZIP_ERRORS = (zipfile.BadZipFile, zlib.error, EOFError, NotImplementedError, RuntimeError)


def describe(error: BaseException) -> str:
    """The message of an error that is not one of ours (an OSError, a zip error)."""
    return str(error) or type(error).__name__


class BackupError(Exception):
    """A backup could not be created or restored.

    A param that is an exception (the cause) is shown with its own message.
    """

    def __init__(self, code: str, **params: object) -> None:
        self.code = code
        self.params = params
        english = {k: describe(v) if isinstance(v, BaseException) else v for k, v in params.items()}
        super().__init__(en.STRINGS[f"error_{code}"].format(**english))


class InvalidBackupError(BackupError):
    """A file is not a valid backup, or is damaged or unsafe."""


class RestoreFailedError(BackupError):
    """A restore failed; ``safety_backup`` holds the config folder as it was before."""

    def __init__(self, error: BaseException, safety_backup: Path) -> None:
        self.error = error
        self.safety_backup = safety_backup
        super().__init__("restore_failed", error=error, path=safety_backup)


class IncompleteSafetyBackupError(BackupError):
    """The safety backup could not read every file, so the restore did not start.

    Nothing was changed. ``skipped`` lists the files (relative to the config folder).
    """

    def __init__(self, skipped: list[str]) -> None:
        self.skipped = skipped
        super().__init__("safety_incomplete", count=len(skipped), files=preview_list(skipped))
