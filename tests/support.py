"""Helpers shared by the tests (importable because pytest adds tests/ to the path)."""

import contextlib
import json
import struct
import zipfile
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

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
            info = zipfile.ZipInfo(name)
            # Stored exactly as given: ZipInfo turns "\\" into "/" on Windows and cuts
            # a name short at "\\0", but backups from elsewhere can hold both.
            info.filename = name
            zf.writestr(info, text)
    return path


def corrupt_member(zip_path: Path, name: str) -> None:
    """Flip a byte in the stored data of one member, as a damaged download would."""
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(name)
    data = bytearray(zip_path.read_bytes())
    # Local file header: 30 bytes, then the file name and the extra field.
    name_len, extra_len = struct.unpack_from("<HH", data, info.header_offset + 26)
    data[info.header_offset + 30 + name_len + extra_len + info.compress_size // 2] ^= 0xFF
    zip_path.write_bytes(data)


def replace_member(zip_path: Path, name: str, text: str) -> None:
    """Replace one member of a zip (rewrites the whole file)."""
    with zipfile.ZipFile(zip_path) as zf:
        members = {n: zf.read(n) for n in zf.namelist()}
    members[name] = text.encode()
    with zipfile.ZipFile(zip_path, "w") as zf:
        for n, data in members.items():
            zf.writestr(n, data)


@contextlib.contextmanager
def unreadable(monkeypatch: pytest.MonkeyPatch, name: str) -> Iterator[None]:
    """Files called ``name`` can't be opened for reading (as files OBS holds locked)."""
    real_open = Path.open

    def open_(self: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
        if self.name == name and "r" in mode:
            raise PermissionError(f"locked: {self}")
        return real_open(self, mode, *args, **kwargs)

    with monkeypatch.context() as m:
        m.setattr(Path, "open", open_)
        yield
