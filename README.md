# Backup & Restore for OBS

## Disclaimer
This Project is **not** associated with the [OBS Studio](https://obsproject.com/) itself. It is an open source tool which helps to create and restore backups.

## Overview
A simple tool with a graphical interface to **back up and restore [OBS Studio](https://obsproject.com/)**: profiles, scene collections (scenes and sources), settings, plugin settings and, optionally, the media files your scenes use.

Works on **Windows** and **Linux**. The interface is in **English** and **German**. macOS is not supported yet.

> **AI disclosure:** Most of the code was written with an AI coding assistant (Claude Code by Anthropic) and is reviewed by the maintainer. See [AI disclosure](#ai-disclosure).

![Backup & Restore for OBS on Windows: the Back up tab with the detected OBS installation, profiles, scene collections and settings to choose from](docs/screenshot.png)

## Features

- **Finds OBS automatically.** It detects a running OBS and uses the config folder that OBS uses, including **portable installs**, **Flatpak** and **Snap**. You can also pick any folder by hand.
- **Choose what to back up:** single profiles, single scene collections, general settings, plugin settings, browser dock logins.
- **Media files, optional.** Images, videos, sounds and other files your sources point to can go into the backup. On restore, files that are missing on the computer are put into a folder you choose, and the scene collections are updated to point there. This makes moving to a new PC easy.
- **Safe restore.**
  - Restoring is blocked while OBS is running, because OBS writes its files when it closes and would overwrite the restore.
  - The current state is backed up before every restore. If that backup can't save a file the restore would replace, nothing is restored.
  - You choose which items to restore.
  - Files that couldn't be read when a backup was made (usually because OBS had them open) are never deleted by restoring that backup. Backups made by older versions don't record this, so restoring them removes no files.
- **Plain zip files.** Every backup is a normal `.zip` with a `manifest.json`, so you can open it without this tool.

## Download

Get the latest version from the [Releases](../../releases) page. No installation is needed.

| System  | File                                  |
|---------|---------------------------------------|
| Windows | `Backup-Restore-for-OBS-windows.exe`  |
| Linux   | `Backup-Restore-for-OBS-linux.tar.gz` |

Each release also has a `SHA256SUMS.txt` for checking the downloads.

The apps are built by GitHub Actions from the source code in this repository ([release workflow](.github/workflows/release.yml)), but they are not code-signed yet. Windows SmartScreen may therefore warn you the first time: click “More info” → “Run anyway”.

### Running on Linux

The archive holds a single program file. Unpack it and start it:

```bash
tar -xzf Backup-Restore-for-OBS-linux.tar.gz
./Backup-Restore-for-OBS
```

You can also start it by double-clicking it in your file manager. To start it from anywhere in a terminal, move it to a folder on your `PATH`, for example `~/.local/bin`.

The app is built on Ubuntu 22.04 and needs glibc 2.35 or newer: Ubuntu 22.04+, Linux Mint 21+, Debian 12+, Fedora 36+ and current Arch all work. On older systems, [run it from source](#run-from-source).

If it doesn't start and the terminal says `Could not load the Qt platform plugin "xcb"`, install the missing library:

| Distribution    | Command                              |
|-----------------|--------------------------------------|
| Ubuntu / Debian | `sudo apt install libxcb-cursor0`    |
| Fedora          | `sudo dnf install xcb-util-cursor`   |
| Arch            | `sudo pacman -S xcb-util-cursor`     |

It finds OBS installed from your distribution's packages, as Flatpak or as Snap.

To uninstall, delete the app. Its settings are stored in the registry under `HKEY_CURRENT_USER\Software\Backup & Restore for OBS` (Windows) or in `~/.config/Backup & Restore for OBS/` (Linux). Your backups stay where you saved them.

## Usage

1. Start Backup & Restore for OBS. It shows the OBS config folder it found and whether OBS is running.
2. **Back up** tab: tick what you want, optionally include media files, and click **Create backup**. Backups go to `Documents/OBS Backups` by default.
3. **Restore** tab: close OBS, pick a backup, tick what you want to restore and click **Restore**. Then start OBS.

> ⚠ **Backups contain secrets:** stream keys (in each profile's `service.json`), the obs-websocket password and, if selected, browser dock logins. Keep backups private, and don't attach them to bug reports.

## What gets backed up

The OBS config folder is in a different place depending on the system:

| System              | OBS config folder                                         |
|---------------------|-----------------------------------------------------------|
| Windows             | `%APPDATA%\obs-studio`                                    |
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
| Installed plugins          | `plugins/` (Linux user plugin folder)                    | on      |
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

## FAQ

### After restoring on another PC, OBS says an encoder is missing

For example: *“The following configured encoders are missing: obs_nvenc_av1_tex, ffmpeg_nvenc. Module "obs-nvenc" was not loaded.”*

The restored profile uses a **hardware encoder** of the graphics card in the old PC, here NVIDIA NVENC. The new PC has different graphics hardware, or no driver for it, so OBS can't use that encoder. The backup is fine; only the encoder choice doesn't fit the new PC.

To fix it, click OK, open **Settings → Output** in OBS and choose an encoder that this PC has, for streaming and for recording:

- **x264**: works on every PC, but uses the CPU.
- **NVIDIA NVENC**, **AMD AMF**, **Intel Quick Sync** or, on Linux, **VA-API**: if the PC has that graphics hardware.

Then click OK. OBS saves the profile and stops showing the message. Your other output settings, such as bitrate and resolution, stay as they were. After a restore, Backup & Restore for OBS lists the profiles that use a hardware encoder.

### Some sources show no image after restoring on another PC

Their media files are missing on the new PC. Include media files when you make the backup, and keep “Restore missing media files” ticked when you restore. After the restore, the app lists media files that are missing and not in the backup; point those sources to the files in OBS. Folders used by slideshow sources are not copied.

### A plugin is missing after restoring

Plugins are programs, not settings, and are installed separately. Only their settings, and on Linux the plugins in your user plugin folder, are in the backup. Install the plugins on the new PC, and their restored settings are used.

### Can I move my setup from Windows to Linux, or the other way round?

Yes. Profiles, scene collections and settings work on both. Media files are restored to a folder you choose, and the scene collections are changed to point there. Hardware encoders and plugins may differ between the systems, see above.

## Privacy

Backup & Restore for OBS does not send any information to other networked systems unless the user specifically requests it. It works only with files on your computer. It has no telemetry, no update check and no accounts.

## AI disclosure

This project was built with the AI coding assistant [Claude Code](https://claude.com/claude-code) by Anthropic.

- **Written with AI:** most of the source code, the tests, the build and release scripts, the German translation and most of this documentation.
- **Done by the maintainer:** the idea and requirements, the decisions on features, naming, licensing and releases, testing with real OBS setups, the screenshots, and reviewing the code.

The maintainer reviews the code and is responsible for it. Commits made with the AI assistant are marked with a `Co-Authored-By: Claude` line in the git history.

Found a bug? Please [open an issue](../../issues).

## Run from source

The project uses [uv](https://docs.astral.sh/uv/) to manage Python, the dependencies and the commands. Install uv, then:

```bash
git clone https://github.com/OliverGras/backup-restore-for-obs.git
cd backup-restore-for-obs
uv sync                          # create .venv with the locked dependencies
uv run backup-restore-for-obs    # start the app
uv run pytest                    # run the tests
```

The project needs **Python 3.15** (set in `.python-version`; uv installs it if needed). It uses 3.15 features such as lazy imports and `frozendict`. Dependency versions are pinned in `uv.lock`. To update them, run `uv lock --upgrade` and commit the new lock file.

Build a standalone app (output in `dist/`):

```bash
uv run python packaging/build.py
```

To release, set the version in [`src/obs_backup/__init__.py`](src/obs_backup/__init__.py), commit, then push a tag with the same version (`git tag 1.0.0 && git push origin 1.0.0`). GitHub Actions builds the apps for Windows and Linux and creates a draft release with them.

## Project layout

```
src/obs_backup/
  obs/              knowledge about OBS Studio
    locator.py        find running OBS and its config folder (standard, portable, Flatpak, Snap)
    config.py         read profiles, scene collections and the OBS version
    media.py          find and rewrite media file paths in scene collections
  backup/           backup files
    layout.py         how a backup zip is organised
    models.py         Selection (what to back up or restore) and result types
    manifest.py       manifest.json inside every backup; listing backups
    collect.py        which files and media a selection covers
    create.py         writing a backup
    restore.py        restoring a backup
  i18n/             UI texts: one file per language (en.py, de.py)
  gui/              PySide6 interface: main window, OBS panel, backup and restore tabs, …
  legal.py          license texts shown under Help → About → Licenses
  licenses/         license texts of the bundled third-party components
packaging/          build script for the standalone apps
tests/              pytest tests, grouped like the code (backup/, obs/, gui/)
```

## Contributing

Issues and pull requests are welcome.

- **Code style:** the code is formatted with [ruff](https://docs.astral.sh/ruff/). Install the git hooks once with `uv run pre-commit install`; they then sort imports and format the code on every commit. CI checks formatting (`uv run ruff format --check`), lint rules (`uv run ruff check`) and types (`uv run pyright`, the checker behind VS Code's Pylance).
- **To add a language**, copy [`src/obs_backup/i18n/en.py`](src/obs_backup/i18n/en.py) to `<language code>.py`, translate the texts and add the module to `_MODULES` in [`src/obs_backup/i18n/__init__.py`](src/obs_backup/i18n/__init__.py). Tests check that no text is missing and that the `{placeholders}` match.

## License

Backup & Restore for OBS is licensed under the [MIT License](LICENSE).

The ready-to-run apps also contain third-party components under their own licenses. Most notably, they use [Qt](https://www.qt.io/) and [PySide6](https://wiki.qt.io/Qt_for_Python) under the GNU LGPL v3. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for the full list, the source code links and the license texts. They can also be read in the app under Help → About Backup & Restore for OBS → Licenses.

Backup & Restore for OBS is an independent project. It is not affiliated with or endorsed by the OBS Project. “OBS” and “OBS Studio” are trademarks of the OBS Project.
