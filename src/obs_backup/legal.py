"""License texts shipped with the app (shown under Help → About → Licenses)."""

import sys
import sysconfig
from pathlib import Path

HERE = Path(__file__).resolve().parent
LICENSES_DIR = HERE / "licenses"
REPO_ROOT = HERE.parent.parent  # source checkout: src/obs_backup -> repo

# Python's license lists the libraries bundled with that particular Python build
# (OpenSSL, libffi, …), so it is taken from the Python in use, not kept in the repo.
PYTHON_LICENSE = "Python-PSF.txt"


def python_license_file() -> Path | None:
    """LICENSE.txt of the running Python (next to python.exe, or in the stdlib folder)."""
    for folder in (Path(sys.base_prefix), Path(sysconfig.get_path("stdlib"))):
        if (folder / "LICENSE.txt").is_file():
            return folder / "LICENSE.txt"
    return None


def license_documents() -> list[tuple[str, Path]]:
    """Our own license, the third-party notices and every bundled license text."""
    docs: list[tuple[str, Path]] = []
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        # In the packaged app the build copies both into the licenses folder.
        for base in (LICENSES_DIR, REPO_ROOT):
            if (base / name).is_file():
                docs.append((name, base / name))
                break
    docs += [(p.name, p) for p in sorted(LICENSES_DIR.glob("*.txt"))]
    # The packaged app has the build's Python license in its licenses folder;
    # when running from source, show the license of the running Python.
    if all(name != PYTHON_LICENSE for name, _ in docs) and (python := python_license_file()):
        docs.append((PYTHON_LICENSE, python))
    return docs
