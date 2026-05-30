"""Course localization — small, extensible, dependency-free.

Mirrors the ecosystem landing's i18n convention so the whole project shares one
mental model:
  - supported languages: en / ru / es (extend by dropping a new JSON catalog)
  - dot-path keys ("modules.m1.title"), JSON catalogs in course-app/i18n/<lang>.json
  - language resolved from explicit arg -> COURSE_LANG env -> default "en"
  - missing keys fall back to English, then to the key itself (never crash a lab)

Add a language: create i18n/<code>.json with the same keys and add the code to
SUPPORTED. Nothing else changes — labs call t(key) and stay language-agnostic.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SUPPORTED = ("en", "ru", "es")
FALLBACK = "en"

_CATALOG_DIR = Path(__file__).resolve().parent.parent / "i18n"
_cache: dict[str, dict[str, Any]] = {}


def available_languages() -> list[str]:
    """Languages that actually have a catalog file on disk."""
    return [c for c in SUPPORTED if (_CATALOG_DIR / f"{c}.json").is_file()]


def resolve_lang(lang: str | None = None) -> str:
    """Pick a language: explicit arg -> COURSE_LANG env -> FALLBACK."""
    cand = (lang or os.environ.get("COURSE_LANG") or FALLBACK).strip().lower()[:2]
    return cand if cand in SUPPORTED else FALLBACK


def _load(lang: str) -> dict[str, Any]:
    if lang in _cache:
        return _cache[lang]
    path = _CATALOG_DIR / f"{lang}.json"
    data: dict[str, Any] = {}
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
    _cache[lang] = data
    return data


def _lookup(dct: dict[str, Any], dotted: str) -> Any:
    node: Any = dct
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


class Translator:
    """Bound to one language; ``t(key, **fmt)`` returns a localized string.

    Resolution order per key: this language -> English -> the key itself.
    ``**fmt`` are applied with str.format, so catalogs may use {placeholders}.
    """

    def __init__(self, lang: str | None = None):
        self.lang = resolve_lang(lang)
        self._primary = _load(self.lang)
        self._fallback = _load(FALLBACK) if self.lang != FALLBACK else self._primary

    def t(self, key: str, **fmt: Any) -> str:
        val = _lookup(self._primary, key)
        if val is None:
            val = _lookup(self._fallback, key)
        if val is None:
            return key  # last resort: surface the key, never raise
        if isinstance(val, str) and fmt:
            try:
                return val.format(**fmt)
            except (KeyError, IndexError):
                return val
        return val

    def __call__(self, key: str, **fmt: Any) -> str:
        return self.t(key, **fmt)


def get_translator(lang: str | None = None) -> Translator:
    return Translator(lang)
