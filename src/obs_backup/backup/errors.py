"""Errors raised while creating or restoring backups."""


class BackupError(Exception):
    """A backup could not be created or restored."""


class InvalidBackupError(BackupError):
    """A file is not a valid backup, or is damaged or unsafe."""
