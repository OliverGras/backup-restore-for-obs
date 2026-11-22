"""Entry point: ``python -m obs_backup`` or the ``obs-backup`` command."""

import sys


def main() -> int:
    from obs_backup.gui import run

    return run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
