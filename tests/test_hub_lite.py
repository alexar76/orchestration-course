"""Tests for hub-lite (M4/M7 fast path)."""

import pytest

pytest.importorskip("fastapi")

from courselib.hub_lite import embedded_hub_lite


def test_hub_lite_discover_invoke_verify():
    with embedded_hub_lite() as hub:
        wk = hub.well_known()
        assert wk.get("name") == "course-hub-lite"
        matches = hub.discover("translate")
        assert matches
        out = hub.invoke("prod-translate", "translate.multi@v2", {"text": "hi"})
        assert out["success"] is True
        assert hub.verify_receipt(out["receipt"])
