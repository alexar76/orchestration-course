"""Tests for M7 trust helpers (stdlib only)."""

from courselib.trust import sign_receipt, tamper_receipt, verify_receipt


def test_sign_and_verify():
    receipt = sign_receipt({"product_id": "p1", "price_usd": 0.01}, "secret")
    assert verify_receipt(receipt, "secret")
    assert not verify_receipt(receipt, "wrong")


def test_tamper_fails_verification():
    receipt = sign_receipt({"product_id": "p1"}, "secret")
    bad = tamper_receipt(receipt, product_id="p2")
    assert not verify_receipt(bad, "secret")
