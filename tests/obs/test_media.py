"""Finding media file paths in scene collections."""

import os
from pathlib import Path

import pytest

from obs_backup.obs.media import file_name, find_media_files, looks_like_local_path


def test_path_heuristic() -> None:
    assert looks_like_local_path("C:/Users/me/a.png")
    assert looks_like_local_path(r"D:\clips\b.mp4")
    assert looks_like_local_path("/home/me/a.png")
    assert looks_like_local_path(r"\\nas\share\c.mp3")
    assert not looks_like_local_path("https://example.com/a.png")
    assert not looks_like_local_path("file:///C:/a.png")
    assert not looks_like_local_path("relative/a.png")
    assert not looks_like_local_path("")


def test_find_media_only_existing(tmp_path: Path) -> None:
    f = tmp_path / "a.png"
    f.write_text("x")
    data = {
        "a": f.as_posix(),
        "b": [{"value": f.as_posix()}],
        "c": (tmp_path / "missing.png").as_posix(),
    }
    assert find_media_files(data) == [f.as_posix()]


def test_file_name_cross_os() -> None:
    assert file_name("C:/Users/me/logo.png") == "logo.png"
    assert file_name(r"C:\Users\me\logo.png") == "logo.png"
    assert file_name("/home/me/logo.png") == "logo.png"


@pytest.mark.skipif(os.name == "nt", reason="C:/... is absolute on Windows")
def test_windows_path_is_not_found_in_the_current_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "C:").mkdir()
    (tmp_path / "C:" / "logo.png").write_text("PNG")
    monkeypatch.chdir(tmp_path)
    assert find_media_files({"file": "C:/logo.png"}) == []
