"""Translations: complete, consistent and matching the texts the code uses."""

import re
import string
from pathlib import Path

import pytest

from obs_backup.i18n import DEFAULT, STRINGS, set_language, system_language, tr

SRC = Path(__file__).resolve().parents[1] / "src" / "obs_backup"
# Keys built at runtime, e.g. tr(f"kind_{inst.kind}").
DYNAMIC_PREFIXES = ("kind_",)


def used_keys() -> set[str]:
    keys = set()
    for path in SRC.rglob("*.py"):
        keys |= set(re.findall(r'\btr\(\s*"([a-z0-9_]+)"', path.read_text(encoding="utf-8")))
    return keys


def placeholders(text: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(text) if name}


@pytest.mark.parametrize("code", sorted(STRINGS))
def test_language_has_every_key(code: str) -> None:
    assert set(STRINGS[code]) == set(STRINGS[DEFAULT])


@pytest.mark.parametrize("code", sorted(STRINGS))
def test_placeholders_match_english(code: str) -> None:
    for key, text in STRINGS[code].items():
        assert placeholders(text) == placeholders(STRINGS[DEFAULT][key]), key


def test_every_used_key_exists() -> None:
    assert used_keys() - set(STRINGS[DEFAULT]) == set()


def test_no_unused_keys() -> None:
    unused = {
        key for key in set(STRINGS[DEFAULT]) - used_keys() if not key.startswith(DYNAMIC_PREFIXES)
    }
    assert unused == set()


def test_system_language() -> None:
    assert system_language("de_DE") == "de"
    assert system_language("en_US") == "en"
    assert system_language("fr_FR") == "en"


def test_tr_falls_back_and_formats() -> None:
    set_language("xx")  # unknown -> English
    assert tr("btn_restore") == "Restore"
    assert tr("media_summary", count=2, size="1 MB") == "2 media files, 1 MB"
    set_language("de")
    assert tr("btn_restore") == "Wiederherstellen"
    set_language(DEFAULT)
