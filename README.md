# OBS Backup & Restore

A simple tool with a graphical interface to **back up and restore [OBS Studio](https://obsproject.com/)**: profiles, scene collections (scenes and sources), settings, plugin settings and, optionally, the media files your scenes use.

Works on **Windows, macOS and Linux**. The interface is in **English** and **German**.

## Features

- **Finds OBS automatically.** It detects a running OBS and uses the config folder that OBS uses, including **portable installs**, **Flatpak** and **Snap**. You can also pick any folder by hand.
- **Choose what to back up:** single profiles, single scene collections, general settings, plugin settings, browser dock logins.
- **Media files, optional.** Images, videos, sounds and other files your sources point to can go into the backup. On restore, files that are missing on the computer are put into a folder you choose, and the scene collections are updated to point there. This makes moving to a new PC easy.
- **Safe restore.**
  - Restoring is blocked while OBS is running, because OBS writes its files when it closes and would overwrite the restore.
  - The current state is backed up before every restore.
  - You choose which items to restore.
- **Plain zip files.** Every backup is a normal `.zip` with a `manifest.json`, so you can open it without this tool.

## Download

Get the latest version from the [Releases](../../releases) page. No installation is needed.

| System  | File                       |
|---------|------------------------------------|
| Windows | `OBS-Backup-Restore-windows.exe`   |
| macOS   | `OBS-Backup-Restore-macos.zip`     |
| Linux   | `OBS-Backup-Restore-linux.tar.gz`  |

Each release also has a `SHA256SUMS.txt` for checking the downloads.

The apps are built by GitHub Actions from the source code in this repository ([release workflow](.github/workflows/release.yml)), but they are not code-signed yet. Windows SmartScreen may therefore warn you the first time: click “More info” → “Run anyway”. On macOS, right-click the app → “Open” the first time.

To uninstall, delete the app. Its settings are stored in the registry under `HKEY_CURRENT_USER\Software\OBS Backup & Restore` (Windows), in a `.plist` file named after OBS Backup & Restore in `~/Library/Preferences/` (macOS) or in `~/.config/OBS Backup & Restore/` (Linux). Your backups stay where you saved them.

## Usage

1. Start OBS Backup & Restore. It shows the OBS config folder it found and whether OBS is running.
2. **Back up** tab: tick what you want, optionally include media files, and click **Create backup**. Backups go to `Documents/OBS Backups` by default.
3. **Restore** tab: close OBS, pick a backup, tick what you want to restore and click **Restore**. Then start OBS.

> ⚠ **Backups contain secrets:** stream keys (in each profile's `service.json`), the obs-websocket password and, if selected, browser dock logins. Keep backups private, and don't attach them to bug reports.

## What gets backed up

The OBS config folder is in a different place depending on the system:

| System              | OBS config folder                                         |
|---------------------|-----------------------------------------------------------|
| Windows             | `%APPDATA%\obs-studio`                                    |
| macOS               | `~/Library/Application Support/obs-studio`                |
| Linux               | `~/.config/obs-studio`                                    |
| Linux (Flatpak)     | `~/.var/app/com.obsproject.Studio/config/obs-studio`      |
| Linux (Snap)        | `~/snap/obs-studio/current/.config/obs-studio`            |
| Portable install    | `<OBS folder>/config/obs-studio`                          |

| Item                       | Files                                                    | Default |
|----------------------------|----------------------------------------------------------|---------|
| Profiles                   | `basic/profiles/<profile>/`                              | on      |
| Scene collections          | `basic/scenes/<name>.json` (scenes, sources, filters, transitions) | on |
| General settings           | `global.ini`, `user.ini`, `plugin_manager/`              | on      |
| Plugin settings            | `plugin_config/*` except `obs-browser`                   | on      |
| Installed plugins          | `plugins/` (macOS / Linux user plugin folder)            | on      |
| Browser source & dock data | `plugin_config/obs-browser/` without caches (cookies, logins) | off |
| Media files                | Files the scene collections refer to by absolute path    | off     |

Not backed up: logs, crash reports, caches, and OBS itself. Plugins installed system-wide (for example in `C:\ProgramData\obs-studio\plugins` or the OBS program folder) are not included. Reinstall them on a new computer. Folders used by slideshow sources are not copied either; only single files are.

### Backup file format

```
obs-backup_2026-11-22_09-36-10.zip
├── manifest.json          what is inside, OBS version, source OS, media list
├── config/…               files from the OBS config folder, same layout
└── media/0001_logo.png    optional media copies
```

## Privacy

OBS Backup & Restore does not send any information to other networked systems unless the user specifically requests it. It works only with files on your computer. It has no telemetry, no update check and no accounts.

## Run from source

Requires Python 3.10 or newer.

```bash
git clone https://github.com/OliverGras/obs_backup_restore.git
cd obs_backup_restore
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
python -m obs_backup      # start the app
pytest                    # run the tests
```

Build a standalone app (output in `dist/`):

```bash
python packaging/build.py
```

Pushing a tag such as `v0.1.0` builds the apps for all three systems through GitHub Actions and creates a draft release with them.

## Project layout

```
src/obs_backup/
  locator.py     find running OBS and its config folder (standard, portable, Flatpak, Snap)
  obs_config.py  read profiles, scene collections and OBS version from a config folder
  media.py       find and rewrite media file paths in scene collections
  archive.py     create and restore backup zips
  i18n.py        English and German UI texts
  gui.py         PySide6 interface
  licenses/      license texts of the bundled third-party components
packaging/       build script for the standalone apps
tests/           pytest tests
```

## Contributing

Issues and pull requests are welcome. **To add a language**, copy the `"en"` block in [`src/obs_backup/i18n.py`](src/obs_backup/i18n.py), translate it and add the language to `LANGUAGES`. A test checks that no text is missing.

## License

OBS Backup & Restore is licensed under the [MIT License](LICENSE).

The ready-to-run apps also contain third-party components under their own licenses. Most notably, they use [Qt](https://www.qt.io/) and [PySide6](https://wiki.qt.io/Qt_for_Python) under the GNU LGPL v3. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the full list, the source code links and the license texts. They can also be read in the app under Help → About OBS Backup & Restore → Licenses.

OBS Backup & Restore is an independent project. It is not affiliated with or endorsed by the OBS Project. “OBS” and “OBS Studio” are trademarks of the OBS Project.
