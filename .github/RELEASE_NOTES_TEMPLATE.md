<!-- REPO_URL is replaced by the release workflow. When copying this by hand, replace it with the repository URL. -->
## Download

| System  | File |
|---------|------|
| Windows | `OBS-Backup-Restore-windows.exe` – just run it, no installation needed |
| macOS   | `OBS-Backup-Restore-macos.zip` – unzip, then right-click the app → Open the first time |
| Linux   | `OBS-Backup-Restore-linux.tar.gz` – unpack and run `OBS-Backup-Restore` |

`SHA256SUMS.txt` lists the checksums of all files.

OBS Backup & Restore backs up and restores OBS Studio profiles, scene collections (scenes and sources), settings, plugin settings and optionally the media files your scenes use. See the [README](REPO_URL/blob/main/README.md) for how to use it.

> ⚠ Backups contain your stream keys and passwords. Keep them private.

The apps are not code-signed yet. Windows SmartScreen may warn you the first time: click “More info” → “Run anyway”.

## Licenses

OBS Backup & Restore is MIT-licensed. The apps include Qt and PySide6 (GNU LGPL v3) and other components; see [THIRD_PARTY_NOTICES.md](REPO_URL/blob/main/THIRD_PARTY_NOTICES.md) or Help → About → Licenses in the app.
