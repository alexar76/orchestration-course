#!/usr/bin/env python3
"""Run course exercises and optionally generate a certificate."""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.certificate import write_certificate
from courselib.exercises import EXERCISES, run_all


def main() -> int:
    p = argparse.ArgumentParser(description="Run orchestration course exercises")
    p.add_argument("--module", choices=sorted(EXERCISES.keys()), help="Run one module exercise")
    p.add_argument("--certificate", metavar="NAME", help="Generate HTML certificate after all exercises pass")
    p.add_argument("--lang", default="en", choices=("en", "ru", "es"))
    p.add_argument("-o", "--out", type=pathlib.Path, default=pathlib.Path("certificate.html"))
    p.add_argument("--skip-check", action="store_true", help="Generate certificate without running exercises")
    args = p.parse_args()

    if args.module:
        fn = EXERCISES[args.module]
        fn()
        print(f"{args.module}: ok")
        return 0

    results = run_all()
    failed = False
    for mod, status in results.items():
        mark = "✓" if status == "ok" else "✗"
        print(f"  {mark} {mod}: {status}")
        if status != "ok":
            failed = True

    if failed:
        print("\nFix failing exercises, then re-run.")
        return 1

    print("\nAll exercises passed.")

    if args.certificate:
        path = write_certificate(
            args.out,
            args.certificate,
            lang=args.lang,
            require_exercises=not args.skip_check,
        )
        print(f"Certificate written: {path.resolve()}")
        print("Open in a browser and Print → Save as PDF for a PDF copy.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
