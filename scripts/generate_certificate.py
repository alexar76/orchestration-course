#!/usr/bin/env python3
"""Generate a personalized course completion certificate (HTML)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from courselib.certificate import write_certificate


def main() -> int:
    p = argparse.ArgumentParser(description="Generate orchestration course certificate")
    p.add_argument("name", help="Learner full name on the certificate")
    p.add_argument("-o", "--out", type=Path, default=Path("certificate.html"))
    p.add_argument("--lang", default="en", choices=("en", "ru", "es"))
    p.add_argument("--skip-check", action="store_true", help="Skip exercise verification (demo only)")
    args = p.parse_args()

    path = write_certificate(
        args.out,
        args.name,
        lang=args.lang,
        require_exercises=not args.skip_check,
    )
    print(f"Wrote {path.resolve()}")
    print("Tip: open in Chrome/Firefox → Print → Save as PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
