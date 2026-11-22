"""Build the standalone app with PyInstaller.

    uv run python packaging/build.py

Output: dist/Backup-Restore-for-OBS.exe (Windows), dist/Backup & Restore for OBS.app (macOS),
dist/Backup-Restore-for-OBS (Linux).
Used locally and by .github/workflows/release.yml.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import PyInstaller.__main__

ROOT = Path(__file__).resolve().parents[1]
# Shown in the Windows file properties. A code signing service will later require
# this to match the registered project name.
PRODUCT_NAME = "Backup & Restore for OBS"
FILE_NAME = "Backup-Restore-for-OBS"
BUILD = ROOT / "build"

# Qt modules the app doesn't use; leaving them out keeps the app small.
EXCLUDED_MODULES = [
    "PySide6.QtNetwork", "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtOpenGL",
    "PySide6.QtSvg", "PySide6.QtPdf", "tkinter",
]


def app_version() -> str:
    text = (ROOT / "src" / "obs_backup" / "__init__.py").read_text(encoding="utf-8")
    return re.search(r'__version__\s*=\s*"([^"]+)"', text).group(1)


def write_windows_version_info(version: str) -> Path:
    """Version resource (file properties → Details) for the Windows .exe."""
    nums = tuple((list(map(int, re.findall(r"\d+", version)[:4])) + [0, 0, 0, 0])[:4])
    content = f"""VSVersionInfo(
  ffi=FixedFileInfo(filevers={nums}, prodvers={nums}, mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('040904B0', [
      StringStruct('CompanyName', 'Oliver Gras'),
      StringStruct('FileDescription', '{PRODUCT_NAME}'),
      StringStruct('FileVersion', '{version}'),
      StringStruct('InternalName', '{FILE_NAME}'),
      StringStruct('LegalCopyright', 'Copyright (c) 2026 Oliver Gras. MIT License.'),
      StringStruct('OriginalFilename', '{FILE_NAME}.exe'),
      StringStruct('ProductName', '{PRODUCT_NAME}'),
      StringStruct('ProductVersion', '{version}')])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""
    BUILD.mkdir(exist_ok=True)
    path = BUILD / "version_info.txt"
    path.write_text(content, encoding="utf-8")
    return path


def main() -> None:
    src = ROOT / "src"
    licenses = "obs_backup/licenses"
    args = [
        str(src / "obs_backup" / "__main__.py"),
        "--noconfirm",
        "--windowed",
        "--name", PRODUCT_NAME if sys.platform == "darwin" else FILE_NAME,
        "--paths", str(src),
        "--add-data", f"{src / 'obs_backup' / 'licenses'}:{licenses}",
        "--add-data", f"{ROOT / 'LICENSE'}:{licenses}",
        "--add-data", f"{ROOT / 'THIRD_PARTY_NOTICES.md'}:{licenses}",
        "--distpath", str(ROOT / "dist"),
        "--workpath", str(BUILD),
        "--specpath", str(BUILD),
    ]
    for module in EXCLUDED_MODULES:
        args += ["--exclude-module", module]
    if sys.platform == "darwin":
        args += ["--osx-bundle-identifier", "io.github.olivergras.backup-restore-for-obs"]
    else:
        args.append("--onefile")
    if sys.platform == "win32":
        args += ["--version-file", str(write_windows_version_info(app_version()))]
    PyInstaller.__main__.run(args + sys.argv[1:])


if __name__ == "__main__":
    main()
