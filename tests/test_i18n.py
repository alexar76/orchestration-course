"""Tests for the course localization system (en/ru/es, extensible)."""

import json
from pathlib import Path

import pytest

from courselib.i18n import (
    FALLBACK,
    SUPPORTED,
    available_languages,
    get_translator,
    resolve_lang,
)

CAT_DIR = Path(__file__).resolve().parent.parent / "i18n"


def _keys(d, prefix=""):
    out = set()
    for k, v in d.items():
        kk = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out |= _keys(v, kk)
        else:
            out.add(kk)
    return out


def test_all_supported_languages_have_catalogs():
    assert set(available_languages()) == set(SUPPORTED)


def test_catalogs_have_identical_key_sets():
    cats = {l: json.loads((CAT_DIR / f"{l}.json").read_text(encoding="utf-8")) for l in SUPPORTED}
    base = _keys(cats[FALLBACK])
    for lang in SUPPORTED:
        assert _keys(cats[lang]) == base, f"{lang} key set differs from {FALLBACK}"


@pytest.mark.parametrize("lang", SUPPORTED)
def test_translator_returns_localized_strings(lang):
    t = get_translator(lang)
    assert t.lang == lang
    title = t("modules.m1.title")
    assert isinstance(title, str) and title and title != "modules.m1.title"


def test_missing_key_falls_back_to_key_name():
    t = get_translator("en")
    assert t("nope.not.here") == "nope.not.here"


def test_unknown_language_falls_back_to_english():
    assert resolve_lang("zz") == "en"
    assert get_translator("zz").lang == "en"


def test_ru_and_es_actually_differ_from_en():
    en = get_translator("en")("modules.m8.title")
    ru = get_translator("ru")("modules.m8.title")
    es = get_translator("es")("modules.m8.title")
    assert en != ru and en != es and ru != es
