"""License texts shipped with the app (shown under Help → About → Licenses)."""

from __future__ import annotations

from pathlib import Path


def license_documents() -> list[tuple[str, Path]]:
    """Our own license, the third-party notices and every bundled license text."""
    here = Path(__file__).resolve().parent
    licenses = here / "licenses"
    repo_root = here.parent.parent  # source checkout: src/obs_backup -> repo
    docs: list[tuple[str, Path]] = []
    for name in ("LICENSE", "THIRD_PARTY_NOTICES.md"):
        # In the packaged app the build copies both into the licenses folder.
        for base in (licenses, repo_root):
            if (base / name).is_file():
                docs.append((name, base / name))
                break
    docs += [(p.name, p) for p in sorted(licenses.glob("*.txt"))]
    return docs
