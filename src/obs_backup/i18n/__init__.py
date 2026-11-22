"""UI texts and the current language.

Each language lives in its own module (``en.py``, ``de.py``) with a ``NAME`` and a
``STRINGS`` dict. To add a language, copy ``en.py`` to ``<code>.py``, translate
the values and add the module to ``_MODULES`` below. Missing keys fall back to
English; a test checks that every language has every key.
"""

import locale

from obs_backup.i18n import de, en

DEFAULT = "en"
_MODULES = frozendict(en=en, de=de)

# Read-only: language code -> display name, and language code -> texts.
LANGUAGES: frozendict[str, str] = frozendict({code: m.NAME for code, m in _MODULES.items()})
STRINGS: frozendict[str, frozendict[str, str]] = frozendict(
    {code: frozendict(m.STRINGS) for code, m in _MODULES.items()}
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
