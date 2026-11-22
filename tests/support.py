"""Helpers shared by the tests (importable because pytest adds tests/ to the path)."""

from pathlib import Path

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
