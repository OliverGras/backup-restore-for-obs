"""English texts. This is the reference language: every key must exist here.

Placeholders in braces ({version}, {count} …) are filled in by the app; keep them
unchanged in translations. "&" in menu texts marks the keyboard shortcut letter.
"""

NAME = "English"

STRINGS: dict[str, str] = {
    # Menus and About box
    "app_title": "Backup & Restore for OBS",
    "menu_file": "&File",
    "menu_open_backup_dir": "Open backup folder",
    "menu_open_config_dir": "Open OBS config folder",
    "menu_quit": "&Quit",
    "menu_language": "&Language",
    "menu_help": "&Help",
    "menu_about": "About Backup & Restore for OBS",
    "about_text": (
        "<b>Backup &amp; Restore for OBS {version}</b><br>Back up and restore OBS "
        "Studio profiles, scene collections, sources and settings.<br><br>Open source "
        "under the MIT license. Uses Qt and PySide6 under the GNU LGPL v3; see "
        "“Licenses”.<br><br>This program does not send any data over the "
        "network.<br><br>Most of the code was written with an AI coding assistant "
        "(Claude Code by Anthropic) and is reviewed by the maintainer.<br><br>Not "
        'affiliated with the OBS Project.<br><br><a href="{homepage}">{homepage}</a>'
    ),
    "btn_licenses": "Licenses",
    "licenses_title": "Licenses",
    # OBS installation panel
    "group_install": "OBS installation",
    "install_label": "Config folder:",
    "btn_browse": "Browse…",
    "btn_refresh": "Refresh",
    "kind_standard": "Standard",
    "kind_portable": "Portable",
    "kind_flatpak": "Flatpak",
    "kind_snap": "Snap",
    "kind_custom": "Chosen manually",
    "running_suffix": "running",
    "not_found_suffix": "not created yet",
    "status_running": "● OBS is running ({exe}). Close OBS before restoring.",
    "status_not_running": "● OBS is not running.",
    "status_version": "OBS version {version}",
    "choose_config_dir": "Choose the OBS config folder (obs-studio)",
    "not_obs_dir_title": "Not an OBS config folder?",
    "not_obs_dir_text": (
        "This folder has no 'basic' subfolder and doesn't look like an OBS config "
        "folder.\n\nUse it anyway?"
    ),
    # Tabs
    "tab_backup": "Back up",
    "tab_restore": "Restore",
    # Selection tree
    "item_profiles": "Profiles",
    "item_scenes": "Scene collections (scenes and sources)",
    "item_global": "General settings",
    "item_global_hint": "global.ini, user.ini, plugin manager",
    "item_plugin_config": "Plugin settings",
    "item_plugin_config_hint": "e.g. obs-websocket, includes its password",
    "item_plugins": "Installed plugins (user folder)",
    "item_browser": "Browser source & dock data",
    "item_browser_hint": "cookies and logins of browser docks; can be large",
    "select_all": "Select all",
    "select_none": "Select none",
    # Back up tab
    "media_checkbox": "Include media files used by the scenes (images, videos, sounds …)",
    "media_summary": "{count} media files, {size}",
    "media_counting": "Counting media files…",
    "backup_dir_label": "Save to:",
    "choose_backup_dir": "Choose the backup folder",
    "btn_backup": "Create backup",
    "secret_warning": "⚠ Backups contain your stream keys and passwords. Don't share them.",
    "backup_running": "Creating backup…",
    "backup_done_title": "Backup created",
    "backup_done_text": "Saved {files} files ({size}) to:\n{path}",
    "backup_skipped": (
        "\n\n{count} files could not be read and were skipped (usually because OBS has "
        "them open; close OBS and back up again to include them):\n{files}"
    ),
    "backup_open_folder": "Open folder",
    "nothing_selected": "Select at least one item.",
    "config_dir_missing": (
        "The selected OBS config folder doesn't exist yet, so there is nothing to back up."
    ),
    "backup_while_running": (
        "OBS is running. Settings changed in the last moments may not be saved to disk "
        "yet. Back up anyway?"
    ),
    # Restore tab
    "backup_file_label": "Backup:",
    "choose_backup_file": "Choose a backup file",
    "backup_filter": "OBS backups (*.zip *.ZIP)",
    "no_backups": "No backups in the backup folder yet. Use “Browse…” to open one.",
    "backup_info": "Created {created} on {os} · OBS {obs} · {media} media files",
    "unknown": "unknown",
    "unusable_names": (
        "{count} profiles or scene collections can't be restored on this system because "
        "of their names: {names}"
    ),
    "invalid_backup": "This file can't be restored:\n{error}",
    "media_restore_checkbox": "Restore missing media files to:",
    "choose_media_dir": "Choose where to put restored media files",
    "safety_checkbox": "Back up the current state first (recommended)",
    "btn_restore": "Restore",
    "restore_blocked": "Close OBS to restore.",
    "restore_confirm_title": "Restore backup?",
    "restore_confirm_text": (
        "The selected items will replace the ones in\n{dir}\n\nProfiles and scene "
        "collections with the same name are overwritten."
    ),
    "restore_running": "Restoring…",
    "restore_done_title": "Restore complete",
    "restore_done_text": "Restored {files} files. Start OBS to use them.",
    "restore_media_done": "\n{count} media files were copied to {dir}.",
    "restore_media_missing": (
        "\n\n{count} media files are missing on this computer and not in the backup. Fix "
        "them in OBS:\n{files}"
    ),
    "restore_kept_current": (
        "\n\n{count} files could not be read when this backup was made, so they are not "
        "in it. Files of those names on this computer were left as they were:\n{files}"
    ),
    "restore_hardware_encoders": (
        "\n\nThese profiles use a hardware encoder:\n{profiles}\nIf this computer has "
        "different graphics hardware, OBS reports the encoder as missing. Then choose "
        "another encoder in OBS under Settings → Output."
    ),
    "restore_safety_done": "\n\nYour previous state was saved to:\n{path}",
    "obs_running_title": "OBS is running",
    "obs_running_text": (
        "OBS writes its files when it closes and would overwrite the restore.\n\nClose "
        "OBS and try again."
    ),
    # Errors and messages
    "error_title": "Error",
    "error_text": "Something went wrong:\n{error}",
    "error_restore_failed": (
        "The restore failed:\n{error}\n\nThe OBS config folder as it was before the "
        "restore is saved in:\n{path}"
    ),
    "error_safety_incomplete": (
        "The current state could not be backed up completely, so nothing was restored. "
        "{count} files could not be read:\n{files}\n\nTo restore without backing up the "
        "current state, untick “Back up the current state first”."
    ),
    "language_changed": "Language changed.",
    "close_while_busy": "Please wait until the backup or restore has finished.",
    # Errors the app words itself (error_<code> of BackupError)
    "error_config_dir_not_found": "OBS config folder not found: {dir}",
    "error_nothing_selected": "Nothing is selected.",
    "error_backup_exists": "A file with this name exists already: {path}",
    "error_backup_in_progress": "Another backup is being written to {path}",
    "error_manifest_missing": (
        "manifest.json is missing: this is not a Backup & Restore for OBS backup."
    ),
    "error_manifest_not_utf8": "manifest.json is not valid UTF-8: {error}",
    "error_manifest_not_json": "manifest.json is not valid JSON: {error}",
    "error_not_a_zip": "This is not a valid zip file: {error}",
    "error_not_a_backup": "This is not a Backup & Restore for OBS backup.",
    "error_format_too_new": (
        "This backup has format {version}, but this version of Backup & Restore for OBS "
        "reads format {supported} at most. Please update the app."
    ),
    "error_manifest_damaged": "manifest.json is damaged: {field} = {value}",
    "error_unsafe_path": "Unsafe path in the backup: {path}",
    "error_unsafe_name": "Unsafe name in the backup: {name}",
    "error_name_not_allowed": "File name not allowed on this system: {path}",
    "error_damaged_scene": "Damaged scene collection in the backup: {name}\n{error}",
    "error_damaged_file": "Damaged file in the backup: {name}\n{error}",
    "error_folder_in_the_way": "Can't restore {path}: a folder of that name is in the way.",
    "error_file_in_the_way": "Can't restore {path}: {folder} is a file, not a folder.",
}
