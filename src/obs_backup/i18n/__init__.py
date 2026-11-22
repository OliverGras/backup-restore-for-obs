"""UI texts and the current language.

Each language lives in its own module (``en.py``, ``de.py``) with a ``NAME`` and a
``STRINGS`` dict. To add a language, copy ``en.py`` to ``<code>.py``, translate
the values and add the module to ``_MODULES`` below. Missing keys fall back to
English; a test checks that every language has every key.
"""

import locale
from collections.abc import Mapping

from obs_backup.i18n import de, en


def _frozen[K, V](mapping: Mapping[K, V]) -> frozendict[K, V]:
    # The typeshed stubs in Pyright 1.1.414 declare frozendict.__init__ without
    # parameters, so type checkers reject frozendict(...) with arguments, although
    # Python accepts it. This helper keeps that workaround in one place.
    return frozendict(mapping)  # pyright: ignore[reportCallIssue]


DEFAULT = "en"
_MODULES = _frozen({"en": en, "de": de})

# Read-only: language code -> display name, and language code -> texts.
LANGUAGES: frozendict[str, str] = _frozen({code: m.NAME for code, m in _MODULES.items()})
STRINGS: frozendict[str, frozendict[str, str]] = _frozen(
    {code: _frozen(m.STRINGS) for code, m in _MODULES.items()}
)

_current = DEFAULT


def system_language(locale_name: str | None = None) -> str:
    """Language code for a locale name such as ``"de_DE"`` (default: the system locale)."""
    if locale_name is None:
        try:
            locale_name = locale.getlocale()[0] or ""
        except ValueError:
            locale_name = ""
    lang = locale_name.lower()
    for code in LANGUAGES:
        if lang.startswith(code):
            return code
    return DEFAULT


def set_language(code: str) -> None:
    global _current
    _current = code if code in STRINGS else DEFAULT


def current_language() -> str:
    return _current


def tr(key: str, **kwargs: object) -> str:
    """The text for ``key`` in the current language, with ``{placeholders}`` filled in."""
    text = STRINGS[_current].get(key) or STRINGS[DEFAULT].get(key, key)
    return text.format(**kwargs) if kwargs else text


def preview_list(items: list[str], limit: int = 10) -> str:
    """The first ``limit`` items, one per line, with "…" if there are more."""
    text = "\n".join(items[:limit])
    return text + "\n…" if len(items) > limit else text
