"""Entry point: ``python -m obs_backup`` or the ``backup-restore-for-obs`` command."""

import sys

lazy from obs_backup.gui import run  # Qt is loaded only when the app actually starts


def main() -> int:
    return run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
