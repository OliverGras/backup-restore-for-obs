"""Helpers shared by the tests (importable because pytest adds tests/ to the path)."""

import json
import zipfile
from pathlib import Path
from typing import Any

from obs_backup import backup
from obs_backup.backup import Selection


def write(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def everything(cfg: Path, media: bool = True) -> Selection:
    """Everything in ``cfg``, including browser data and (optionally) media."""
    sel = backup.full_selection(cfg)
    sel.browser_data = True
    sel.media = media
    return sel


def craft_backup(
    path: Path, manifest: dict[str, Any] | bytes, members: dict[str, str] | None = None
) -> Path:
    """A hand-made backup zip, e.g. a damaged or malicious one.

    ``manifest`` is merged into a minimal valid manifest, or used as raw bytes.
    """
    if isinstance(manifest, dict):
        manifest = json.dumps({"format": "obs-backup", "format_version": 1, **manifest}).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("manifest.json", manifest)
        for name, text in (members or {}).items():
            zf.writestr(name, text)
    return path


def replace_member(zip_path: Path, name: str, text: str) -> None:
    """Replace one member of a zip (rewrites the whole file)."""
    with zipfile.ZipFile(zip_path) as zf:
        members = {n: zf.read(n) for n in zf.namelist()}
    members[name] = text.encode()
    with zipfile.ZipFile(zip_path, "w") as zf:
        for n, data in members.items():
            zf.writestr(n, data)
