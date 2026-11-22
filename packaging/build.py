"""Build the standalone app with PyInstaller.

    uv run python packaging/build.py

Output: dist/Backup-Restore-for-OBS.exe (Windows) or dist/Backup-Restore-for-OBS (Linux).
macOS is not supported yet.
Used locally and by .github/workflows/release.yml.
"""

import re
import shutil
import sys
from pathlib import Path

import PyInstaller.__main__

from obs_backup.legal import PYTHON_LICENSE, python_license_file

ROOT = Path(__file__).resolve().parents[1]
# Shown in the Windows file properties. A code signing service will later require
# this to match the registered project name.
PRODUCT_NAME = "Backup & Restore for OBS"
FILE_NAME = "Backup-Restore-for-OBS"
BUILD = ROOT / "build"

# Qt modules the app doesn't use; leaving them out keeps the app small.
EXCLUDED_MODULES = [
    "PySide6.QtNetwork",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtOpenGL",
    "PySide6.QtSvg",
    "PySide6.QtPdf",
    "tkinter",
]


def app_version() -> str:
    text = (ROOT / "src" / "obs_backup" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if match is None:
        sys.exit("__version__ not found in src/obs_backup/__init__.py")
    return match.group(1)


def write_windows_version_info(version: str) -> Path:
    """Version resource (file properties → Details) for the Windows .exe.

    The numeric file version holds the release numbers only: 1.0.0rc1 -> 1.0.0.0
    (taking every number would make it 1.0.0.1). The text fields keep the full version.
    """
    release = re.match(r"\d+(?:\.\d+)*", version)
    numbers = [int(n) for n in release.group().split(".")] if release else []
    nums = tuple((numbers + [0, 0, 0, 0])[:4])
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


def copy_python_license() -> Path:
    """The license of the Python being bundled; it lists that build's own libraries.

    Release builds use the official python.org Python (GitHub Actions). Other Python
    builds, such as the one uv installs, list different libraries in their license.
    """
    source = python_license_file()
    if source is None:
        sys.exit("Python's LICENSE.txt was not found, but it must be bundled with the app.")
    target = BUILD / "licenses" / PYTHON_LICENSE
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    return target


def main() -> None:
    src = ROOT / "src"
    licenses = "obs_backup/licenses"
    args = [
        str(src / "obs_backup" / "__main__.py"),
        "--noconfirm",
        "--windowed",
        "--name",
        FILE_NAME,
        "--onefile",
        "--paths",
        str(src),
        "--add-data",
        f"{src / 'obs_backup' / 'licenses'}:{licenses}",
        "--add-data",
        f"{ROOT / 'LICENSE'}:{licenses}",
        "--add-data",
        f"{ROOT / 'THIRD_PARTY_NOTICES.md'}:{licenses}",
        "--add-data",
        f"{copy_python_license()}:{licenses}",
        "--distpath",
        str(ROOT / "dist"),
        "--workpath",
        str(BUILD),
        "--specpath",
        str(BUILD),
    ]
    for module in EXCLUDED_MODULES:
        args += ["--exclude-module", module]
    if sys.platform == "win32":
        args += ["--version-file", str(write_windows_version_info(app_version()))]
    PyInstaller.__main__.run(args + sys.argv[1:])


if __name__ == "__main__":
    main()
