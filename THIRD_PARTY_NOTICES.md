# Third-party notices

Backup & Restore for OBS's own source code is licensed under the [MIT License](LICENSE).

The ready-to-run apps (for example `Backup-Restore-for-OBS-windows.exe`) also contain the
components listed below, each under its own license. Their full license texts
are in [`src/obs_backup/licenses/`](src/obs_backup/licenses/). They are built
into the app as well: **Help → About Backup & Restore for OBS → Licenses**.

| Component | Used for | License | License text |
|-----------|----------|---------|--------------|
| [Qt 6](https://www.qt.io/) (QtCore, QtGui, QtWidgets and their platform plugins) | User interface | GNU LGPL v3 | `LGPL-3.0.txt`, `GPL-3.0.txt` |
| [PySide6 / Shiboken6](https://wiki.qt.io/Qt_for_Python) | Python bindings for Qt | GNU LGPL v3 | `LGPL-3.0.txt`, `GPL-3.0.txt` |
| [psutil](https://github.com/giampaolo/psutil) | Finding the running OBS process | BSD 3-Clause | `psutil-BSD-3-Clause.txt` |
| [Python](https://www.python.org/) runtime and standard library, including bzip2, libffi, OpenSSL, xz and zlib | Running the app | PSF License and the licenses listed in that file | `Python-PSF.txt` |
| [PyInstaller](https://pyinstaller.org/) bootloader | Starting the single-file app | GPL v2 or later **with the bootloader exception**, which allows distribution under any license | `PyInstaller-GPL-2.0-with-exception.txt` |
| Microsoft Visual C++ runtime (`vcruntime140.dll`, `msvcp140.dll`) | Windows runtime | Microsoft redistributable | – |

## Qt and PySide6 (LGPL v3)

The apps use Qt and PySide6 under the
[GNU Lesser General Public License v3](https://www.gnu.org/licenses/lgpl-3.0.html).
Neither has been modified.

- Qt source code: <https://download.qt.io/official_releases/qt/> and <https://code.qt.io/>
- PySide6 source code: <https://code.qt.io/cgit/pyside/pyside-setup.git/>
- Third-party code inside Qt (for example FreeType, HarfBuzz, libpng, libjpeg, PCRE2, zlib):
  <https://doc.qt.io/qt-6/licenses-used-in-qt.html>

The LGPL lets you use a modified version of these libraries with Backup & Restore for OBS.
Because the app's complete source code is in this repository, you can do that
by installing your own Qt / PySide6 build and running or rebuilding the app as
described in the [README](README.md#run-from-source).

## OBS Studio

Backup & Restore for OBS is an independent project and contains no code from OBS Studio. It is
not affiliated with or endorsed by the OBS Project. “OBS” and “OBS Studio” are
trademarks of the OBS Project, used here only to say which software this tool
works with.
