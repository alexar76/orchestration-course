"""Trust, verification & provenance helpers (M7).

Stdlib-only signed receipts for teaching verification without heavy SDK deps.
Production AIMarket receipts use the same *idea*: payload + nonce + signature.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from typing import Any


def sign_receipt(payload: dict[str, Any], secret: str) -> dict[str, Any]:
    """Attach ``nonce`` and HMAC-SHA256 ``signature`` to a receipt payload."""
    body = dict(payload)
    body["nonce"] = secrets.token_hex(8)
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    sig = hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    body["signature"] = sig
    return body


def verify_receipt(receipt: dict[str, Any], secret: str) -> bool:
    """Return True when the receipt signature matches the payload."""
    if "signature" not in receipt or "nonce" not in receipt:
        return False
    sig = receipt["signature"]
    body = {k: v for k, v in receipt.items() if k != "signature"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def tamper_receipt(receipt: dict[str, Any], **changes: Any) -> dict[str, Any]:
    """Demo helper: mutate fields without re-signing (should fail verification)."""
    bad = dict(receipt)
    bad.update(changes)
    return bad
