#!/usr/bin/env python3
"""Build GitHub Pages site and Colab notebooks from course sources."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def main() -> None:
    for name in ("build_site.py", "labs_to_notebooks.py"):
        script = SCRIPTS / name
        print(f"==> {script.name}")
        subprocess.run([sys.executable, str(script)], check=True, cwd=ROOT)
    print("Done: site/ + notebooks/")


if __name__ == "__main__":
    main()
