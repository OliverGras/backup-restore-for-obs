"""The license texts shown in the app are all present."""

from obs_backup.legal import license_documents

REQUIRED = (
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "LGPL-3.0.txt",
    "GPL-3.0.txt",
    "psutil-BSD-3-Clause.txt",
    "Python-PSF.txt",
    "PyInstaller-GPL-2.0-with-exception.txt",
)


def test_license_texts_present() -> None:
    names = [name for name, _ in license_documents()]
    for required in REQUIRED:
        assert required in names
