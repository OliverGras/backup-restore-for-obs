"""UI texts in English and German.

To add a language, copy the ``"en"`` block, translate the values and add the
language's name to ``LANGUAGES``. Missing keys fall back to English.
"""

from __future__ import annotations

import locale

LANGUAGES = {"en": "English", "de": "Deutsch"}

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "app_title": "OBS Backup",
        "menu_file": "&File",
        "menu_open_backup_dir": "Open backup folder",
        "menu_open_config_dir": "Open OBS config folder",
        "menu_quit": "&Quit",
        "menu_language": "&Language",
        "menu_help": "&Help",
        "menu_about": "About OBS Backup",
        "about_text": "<b>OBS Backup {version}</b><br>Back up and restore OBS Studio profiles, "
                      "scene collections, sources and settings.<br><br>"
                      "Open source under the MIT license. Uses Qt and PySide6 under the GNU LGPL v3; "
                      "see “Licenses”.<br><br>"
                      "This program does not send any data over the network.<br><br>"
                      "Not affiliated with the OBS Project.",
        "btn_licenses": "Licenses",
        "licenses_title": "Licenses",

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
        "not_obs_dir_text": "This folder has no 'basic' subfolder and doesn't look like an OBS config "
                            "folder.\n\nUse it anyway?",

        "tab_backup": "Back up",
        "tab_restore": "Restore",

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

        "media_checkbox": "Include media files used by the scenes (images, videos, sounds …)",
        "media_scanning": "Looking for media files…",
        "media_summary": "{count} media files, {size}",
        "backup_dir_label": "Save to:",
        "choose_backup_dir": "Choose the backup folder",
        "btn_backup": "Create backup",
        "secret_warning": "⚠ Backups contain your stream keys and passwords. Don't share them.",
        "backup_running": "Creating backup…",
        "backup_done_title": "Backup created",
        "backup_done_text": "Saved {files} files ({size}) to:\n{path}",
        "backup_skipped": "\n\n{count} files could not be read and were skipped (usually because OBS "
                          "has them open; close OBS and back up again to include them):\n{files}",
        "backup_open_folder": "Open folder",
        "nothing_selected": "Select at least one item.",
        "backup_while_running": "OBS is running. Settings changed in the last moments may not be "
                                "saved to disk yet. Back up anyway?",

        "backup_file_label": "Backup:",
        "choose_backup_file": "Choose a backup file",
        "backup_filter": "OBS backups (*.zip)",
        "no_backups": "No backups in the backup folder yet. Use “Browse…” to open one.",
        "backup_info": "Created {created} on {os} · OBS {obs} · {media} media files",
        "unknown": "unknown",
        "invalid_backup": "This file can't be restored:\n{error}",
        "media_restore_checkbox": "Restore missing media files to:",
        "choose_media_dir": "Choose where to put restored media files",
        "safety_checkbox": "Back up the current state first (recommended)",
        "btn_restore": "Restore",
        "restore_blocked": "Close OBS to restore.",
        "restore_confirm_title": "Restore backup?",
        "restore_confirm_text": "The selected items will replace the ones in\n{dir}\n\n"
                                "Profiles and scene collections with the same name are overwritten.",
        "restore_running": "Restoring…",
        "safety_running": "Backing up the current state…",
        "restore_done_title": "Restore complete",
        "restore_done_text": "Restored {files} files. Start OBS to use them.",
        "restore_media_done": "\n{count} media files were copied to {dir}.",
        "restore_media_missing": "\n\n{count} media files are missing on this computer and not in "
                                 "the backup. Fix them in OBS:\n{files}",
        "restore_safety_done": "\n\nYour previous state was saved to:\n{path}",
        "obs_running_title": "OBS is running",
        "obs_running_text": "OBS writes its files when it closes and would overwrite the restore.\n\n"
                            "Close OBS and try again.",

        "error_title": "Error",
        "error_text": "Something went wrong:\n{error}",
        "language_changed": "Language changed.",
    },
    "de": {
        "app_title": "OBS Backup",
        "menu_file": "&Datei",
        "menu_open_backup_dir": "Backup-Ordner öffnen",
        "menu_open_config_dir": "OBS-Konfigurationsordner öffnen",
        "menu_quit": "&Beenden",
        "menu_language": "&Sprache",
        "menu_help": "&Hilfe",
        "menu_about": "Über OBS Backup",
        "about_text": "<b>OBS Backup {version}</b><br>Sichern und Wiederherstellen von OBS-Studio-Profilen, "
                      "Szenensammlungen, Quellen und Einstellungen.<br><br>"
                      "Open Source unter der MIT-Lizenz. Verwendet Qt und PySide6 unter der GNU LGPL v3; "
                      "siehe „Lizenzen“.<br><br>"
                      "Dieses Programm sendet keine Daten über das Netzwerk.<br><br>"
                      "Kein offizielles Produkt des OBS-Projekts.",
        "btn_licenses": "Lizenzen",
        "licenses_title": "Lizenzen",

        "group_install": "OBS-Installation",
        "install_label": "Konfigurationsordner:",
        "btn_browse": "Durchsuchen…",
        "btn_refresh": "Aktualisieren",
        "kind_standard": "Standard",
        "kind_portable": "Portabel",
        "kind_flatpak": "Flatpak",
        "kind_snap": "Snap",
        "kind_custom": "Manuell gewählt",
        "running_suffix": "läuft",
        "not_found_suffix": "noch nicht angelegt",
        "status_running": "● OBS läuft ({exe}). Vor dem Wiederherstellen OBS schließen.",
        "status_not_running": "● OBS läuft nicht.",
        "status_version": "OBS-Version {version}",
        "choose_config_dir": "OBS-Konfigurationsordner (obs-studio) wählen",
        "not_obs_dir_title": "Kein OBS-Konfigurationsordner?",
        "not_obs_dir_text": "Dieser Ordner hat keinen Unterordner „basic“ und sieht nicht wie ein "
                            "OBS-Konfigurationsordner aus.\n\nTrotzdem verwenden?",

        "tab_backup": "Sichern",
        "tab_restore": "Wiederherstellen",

        "item_profiles": "Profile",
        "item_scenes": "Szenensammlungen (Szenen und Quellen)",
        "item_global": "Allgemeine Einstellungen",
        "item_global_hint": "global.ini, user.ini, Plugin-Manager",
        "item_plugin_config": "Plugin-Einstellungen",
        "item_plugin_config_hint": "z. B. obs-websocket, inklusive Passwort",
        "item_plugins": "Installierte Plugins (Benutzerordner)",
        "item_browser": "Daten von Browserquellen & Docks",
        "item_browser_hint": "Cookies und Logins der Browser-Docks; kann groß sein",
        "select_all": "Alle auswählen",
        "select_none": "Keine auswählen",

        "media_checkbox": "Mediendateien der Szenen einschließen (Bilder, Videos, Sounds …)",
        "media_scanning": "Suche Mediendateien…",
        "media_summary": "{count} Mediendateien, {size}",
        "backup_dir_label": "Speichern in:",
        "choose_backup_dir": "Backup-Ordner wählen",
        "btn_backup": "Backup erstellen",
        "secret_warning": "⚠ Backups enthalten deine Stream-Keys und Passwörter. Gib sie nicht weiter.",
        "backup_running": "Backup wird erstellt…",
        "backup_done_title": "Backup erstellt",
        "backup_done_text": "{files} Dateien ({size}) gespeichert in:\n{path}",
        "backup_skipped": "\n\n{count} Dateien konnten nicht gelesen werden und fehlen (meist, weil OBS "
                          "sie geöffnet hat; OBS schließen und erneut sichern):\n{files}",
        "backup_open_folder": "Ordner öffnen",
        "nothing_selected": "Wähle mindestens einen Eintrag aus.",
        "backup_while_running": "OBS läuft. Gerade erst geänderte Einstellungen sind evtl. noch nicht "
                                "gespeichert. Trotzdem sichern?",

        "backup_file_label": "Backup:",
        "choose_backup_file": "Backup-Datei wählen",
        "backup_filter": "OBS-Backups (*.zip)",
        "no_backups": "Noch keine Backups im Backup-Ordner. Mit „Durchsuchen…“ eins öffnen.",
        "backup_info": "Erstellt {created} unter {os} · OBS {obs} · {media} Mediendateien",
        "unknown": "unbekannt",
        "invalid_backup": "Diese Datei kann nicht wiederhergestellt werden:\n{error}",
        "media_restore_checkbox": "Fehlende Mediendateien wiederherstellen nach:",
        "choose_media_dir": "Ordner für wiederhergestellte Mediendateien wählen",
        "safety_checkbox": "Vorher den aktuellen Stand sichern (empfohlen)",
        "btn_restore": "Wiederherstellen",
        "restore_blocked": "Zum Wiederherstellen OBS schließen.",
        "restore_confirm_title": "Backup wiederherstellen?",
        "restore_confirm_text": "Die ausgewählten Einträge ersetzen die in\n{dir}\n\n"
                                "Profile und Szenensammlungen mit gleichem Namen werden überschrieben.",
        "restore_running": "Wird wiederhergestellt…",
        "safety_running": "Aktueller Stand wird gesichert…",
        "restore_done_title": "Wiederherstellung abgeschlossen",
        "restore_done_text": "{files} Dateien wiederhergestellt. Starte OBS, um sie zu nutzen.",
        "restore_media_done": "\n{count} Mediendateien wurden nach {dir} kopiert.",
        "restore_media_missing": "\n\n{count} Mediendateien fehlen auf diesem Computer und sind nicht "
                                 "im Backup. Bitte in OBS korrigieren:\n{files}",
        "restore_safety_done": "\n\nDein vorheriger Stand wurde gesichert unter:\n{path}",
        "obs_running_title": "OBS läuft",
        "obs_running_text": "OBS speichert seine Dateien beim Beenden und würde die Wiederherstellung "
                            "überschreiben.\n\nBitte OBS schließen und erneut versuchen.",

        "error_title": "Fehler",
        "error_text": "Etwas ist schiefgelaufen:\n{error}",
        "language_changed": "Sprache geändert.",
    },
}

_current = "en"


def system_language(locale_name: str | None = None) -> str:
    """Language code for a locale name such as ``"de_DE"`` (default: the system locale)."""
    if locale_name is None:
        try:
            locale_name = locale.getlocale()[0] or ""
        except ValueError:
            locale_name = ""
    lang = locale_name.lower()
    for code in LANGUAGES:
        if lang.startswith(code):
            return code
    return "en"


def set_language(code: str) -> None:
    global _current
    _current = code if code in STRINGS else "en"


def current_language() -> str:
    return _current


def tr(key: str, **kwargs: object) -> str:
    text = STRINGS.get(_current, {}).get(key) or STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def format_size(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"
