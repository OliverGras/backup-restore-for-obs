"""German texts (Deutsch)."""

NAME = "Deutsch"

STRINGS: dict[str, str] = {
    # Menus and About box
    "app_title": "Backup & Restore for OBS",
    "menu_file": "&Datei",
    "menu_open_backup_dir": "Backup-Ordner öffnen",
    "menu_open_config_dir": "OBS-Konfigurationsordner öffnen",
    "menu_quit": "&Beenden",
    "menu_language": "&Sprache",
    "menu_help": "&Hilfe",
    "menu_about": "Über Backup & Restore for OBS",
    "about_text": (
        "<b>Backup &amp; Restore for OBS {version}</b><br>Sichern und Wiederherstellen "
        "von OBS-Studio-Profilen, Szenensammlungen, Quellen und "
        "Einstellungen.<br><br>Open Source unter der MIT-Lizenz. Verwendet Qt und "
        "PySide6 unter der GNU LGPL v3; siehe „Lizenzen“.<br><br>Dieses Programm sendet "
        "keine Daten über das Netzwerk.<br><br>Der Großteil des Codes wurde mit einem "
        "KI-Programmierassistenten (Claude Code von Anthropic) geschrieben und wird vom "
        "Maintainer geprüft.<br><br>Kein offizielles Produkt des "
        'OBS-Projekts.<br><br><a href="{homepage}">{homepage}</a>'
    ),
    "btn_licenses": "Lizenzen",
    "licenses_title": "Lizenzen",
    # OBS installation panel
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
    "not_obs_dir_text": (
        "Dieser Ordner hat keinen Unterordner „basic“ und sieht nicht wie ein "
        "OBS-Konfigurationsordner aus.\n\nTrotzdem verwenden?"
    ),
    # Tabs
    "tab_backup": "Sichern",
    "tab_restore": "Wiederherstellen",
    # Selection tree
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
    # Back up tab
    "media_checkbox": "Mediendateien der Szenen einschließen (Bilder, Videos, Sounds …)",
    "media_summary": "{count} Mediendateien, {size}",
    "media_counting": "Mediendateien werden gezählt…",
    "backup_dir_label": "Speichern in:",
    "choose_backup_dir": "Backup-Ordner wählen",
    "btn_backup": "Backup erstellen",
    "secret_warning": "⚠ Backups enthalten deine Stream-Keys und Passwörter. Gib sie nicht weiter.",
    "backup_running": "Backup wird erstellt…",
    "backup_done_title": "Backup erstellt",
    "backup_done_text": "{files} Dateien ({size}) gespeichert in:\n{path}",
    "backup_skipped": (
        "\n\n{count} Dateien konnten nicht gelesen werden und fehlen (meist, weil OBS sie "
        "geöffnet hat; OBS schließen und erneut sichern):\n{files}"
    ),
    "backup_open_folder": "Ordner öffnen",
    "nothing_selected": "Wähle mindestens einen Eintrag aus.",
    "config_dir_missing": (
        "Der gewählte OBS-Konfigurationsordner existiert noch nicht, es gibt also nichts "
        "zu sichern."
    ),
    "backup_while_running": (
        "OBS läuft. Gerade erst geänderte Einstellungen sind evtl. noch nicht "
        "gespeichert. Trotzdem sichern?"
    ),
    # Restore tab
    "backup_file_label": "Backup:",
    "choose_backup_file": "Backup-Datei wählen",
    "backup_filter": "OBS-Backups (*.zip *.ZIP)",
    "no_backups": "Noch keine Backups im Backup-Ordner. Mit „Durchsuchen…“ eins öffnen.",
    "backup_info": "Erstellt {created} unter {os} · OBS {obs} · {media} Mediendateien",
    "unknown": "unbekannt",
    "unusable_names": (
        "{count} Profile oder Szenensammlungen können auf diesem System wegen ihres "
        "Namens nicht wiederhergestellt werden: {names}"
    ),
    "invalid_backup": "Diese Datei kann nicht wiederhergestellt werden:\n{error}",
    "media_restore_checkbox": "Fehlende Mediendateien wiederherstellen nach:",
    "choose_media_dir": "Ordner für wiederhergestellte Mediendateien wählen",
    "safety_checkbox": "Vorher den aktuellen Stand sichern (empfohlen)",
    "btn_restore": "Wiederherstellen",
    "restore_blocked": "Zum Wiederherstellen OBS schließen.",
    "restore_confirm_title": "Backup wiederherstellen?",
    "restore_confirm_text": (
        "Die ausgewählten Einträge ersetzen die in\n{dir}\n\nProfile und Szenensammlungen "
        "mit gleichem Namen werden überschrieben."
    ),
    "restore_running": "Wird wiederhergestellt…",
    "restore_done_title": "Wiederherstellung abgeschlossen",
    "restore_done_text": "{files} Dateien wiederhergestellt. Starte OBS, um sie zu nutzen.",
    "restore_media_done": "\n{count} Mediendateien wurden nach {dir} kopiert.",
    "restore_media_missing": (
        "\n\n{count} Mediendateien fehlen auf diesem Computer und sind nicht im Backup. "
        "Bitte in OBS korrigieren:\n{files}"
    ),
    "restore_kept_current": (
        "\n\n{count} Dateien konnten beim Erstellen dieses Backups nicht gelesen werden und "
        "fehlen darin. Gleichnamige Dateien auf diesem Computer blieben unverändert:\n{files}"
    ),
    "restore_hardware_encoders": (
        "\n\nDiese Profile nutzen einen Hardware-Kodierer:\n{profiles}\nHat dieser Computer "
        "andere Grafikhardware, meldet OBS den Kodierer als fehlend. Wähle dann in OBS "
        "unter Einstellungen → Ausgabe einen anderen Kodierer."
    ),
    "restore_safety_done": "\n\nDein vorheriger Stand wurde gesichert unter:\n{path}",
    "obs_running_title": "OBS läuft",
    "obs_running_text": (
        "OBS speichert seine Dateien beim Beenden und würde die Wiederherstellung "
        "überschreiben.\n\nBitte OBS schließen und erneut versuchen."
    ),
    # Errors and messages
    "error_title": "Fehler",
    "error_text": "Etwas ist schiefgelaufen:\n{error}",
    "error_restore_failed": (
        "Die Wiederherstellung ist fehlgeschlagen:\n{error}\n\nDer "
        "OBS-Konfigurationsordner vor der Wiederherstellung ist gesichert unter:\n{path}"
    ),
    "error_safety_incomplete": (
        "Der aktuelle Stand konnte nicht vollständig gesichert werden, daher wurde nichts "
        "wiederhergestellt. {count} Dateien konnten nicht gelesen werden:\n{files}\n\n"
        "Um ohne Sicherung des aktuellen Stands wiederherzustellen, „Vorher den aktuellen "
        "Stand sichern“ abwählen."
    ),
    "language_changed": "Sprache geändert.",
    "close_while_busy": "Bitte warte, bis das Backup oder die Wiederherstellung fertig ist.",
    # Fehler, die die App selbst formuliert (error_<code> von BackupError)
    "error_config_dir_not_found": "OBS-Konfigurationsordner nicht gefunden: {dir}",
    "error_nothing_selected": "Nichts ausgewählt.",
    "error_backup_exists": "Eine Datei mit diesem Namen gibt es schon: {path}",
    "error_backup_in_progress": "Ein anderes Backup wird gerade nach {path} geschrieben.",
    "error_manifest_missing": (
        "manifest.json fehlt: Das ist kein Backup von Backup & Restore for OBS."
    ),
    "error_manifest_not_utf8": "manifest.json ist kein gültiges UTF-8: {error}",
    "error_manifest_not_json": "manifest.json ist kein gültiges JSON: {error}",
    "error_not_a_zip": "Das ist keine gültige ZIP-Datei: {error}",
    "error_not_a_backup": "Das ist kein Backup von Backup & Restore for OBS.",
    "error_format_too_new": (
        "Dieses Backup hat das Format {version}, diese Version von Backup & Restore for "
        "OBS liest höchstens Format {supported}. Bitte die App aktualisieren."
    ),
    "error_manifest_damaged": "manifest.json ist beschädigt: {field} = {value}",
    "error_unsafe_path": "Unsicherer Pfad im Backup: {path}",
    "error_unsafe_name": "Unsicherer Name im Backup: {name}",
    "error_name_not_allowed": "Dieser Dateiname ist auf diesem System nicht erlaubt: {path}",
    "error_damaged_scene": "Beschädigte Szenensammlung im Backup: {name}\n{error}",
    "error_damaged_file": "Beschädigte Datei im Backup: {name}\n{error}",
    "error_folder_in_the_way": (
        "{path} kann nicht wiederhergestellt werden: Ein Ordner mit diesem Namen ist im Weg."
    ),
    "error_file_in_the_way": (
        "{path} kann nicht wiederhergestellt werden: {folder} ist eine Datei, kein Ordner."
    ),
}
