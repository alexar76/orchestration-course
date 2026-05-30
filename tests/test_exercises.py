"""Tests for DIY exercises and certificate generation."""

from courselib.certificate import certificate_id, render_html, write_certificate
from courselib.exercises import all_passed, run_all


def test_all_exercises_pass():
    results = run_all()
    assert all_passed(results), results


def test_certificate_html_contains_name():
    html = render_html("Ada Lovelace", lang="en")
    assert "Ada Lovelace" in html
    assert "Certificate of Completion" in html


def test_certificate_id_is_stable():
    assert certificate_id("Test User") == certificate_id("Test User")


def test_write_certificate_skip_check(tmp_path):
    out = tmp_path / "cert.html"
    write_certificate(out, "Demo Learner", require_exercises=False)
    assert out.exists()
    assert "Demo Learner" in out.read_text(encoding="utf-8")
