"""PySide6 user interface.

- ``app``:             start the application
- ``main_window``:     menus, panel, tabs, status bar; wires the parts together
- ``install_panel``:   choose the OBS config folder, show whether OBS is running
- ``backup_tab``:      choose what to back up and create the backup
- ``restore_tab``:     choose a backup and restore it
- ``selection_tree``:  checkable tree of profiles, scene collections and settings
- ``widgets``:         reusable widgets (folder field with “Browse…”)
- ``tasks``:           run backup and restore in a background thread
- ``settings``:        values remembered between starts
- ``about``, ``licenses_dialog``: About box and license viewer
"""

from obs_backup.gui.app import run

__all__ = ["run"]
