#!/usr/bin/env python3
"""Convert runnable lab scripts into Colab-ready Jupyter notebooks."""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LABS_DIR = ROOT / "labs"
OUT_DIR = ROOT / "notebooks"

GITHUB_REPO = "alexar76/orchestration-course"

LABS = [
    {"stem": "lab01_agent_and_tool", "sandbox": False},
    {"stem": "lab02_topologies", "sandbox": False},
    {"stem": "lab03_handoff", "sandbox": False},
    {"stem": "lab04_discover_invoke", "sandbox": True},
    {"stem": "lab08_metered_economy", "sandbox": True},
]


def _strip_bootstrap(src: str) -> str:
    """Drop sys.path bootstrap used for in-repo runs."""
    lines: list[str] = []
    for line in src.splitlines():
        stripped = line.strip()
        if "sys.path.insert" in line:
            continue
        if stripped in {"import pathlib", "import sys"}:
            continue
        lines.append(line)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines)


def _extract_body(stem: str) -> tuple[str, str]:
    path = LABS_DIR / f"{stem}.py"
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    doc = (ast.get_docstring(tree) or "").strip()

    body_lines: list[str] = []
    in_main_guard = False
    for line in src.splitlines():
        if line.startswith('if __name__ == "__main__"'):
            in_main_guard = True
            continue
        if in_main_guard:
            continue
        body_lines.append(line)

    body = _strip_bootstrap("\n".join(body_lines)).strip()
    body = body.rstrip() + "\n\nmain()\n"
    return doc, body


def _setup_cell(sandbox: bool) -> str:
    extra = "[sandbox]" if sandbox else ""
    return textwrap.dedent(
        f"""\
        # Setup — run this cell once per session
        import os
        import subprocess
        import sys

        REPO = "https://github.com/{GITHUB_REPO}.git"
        DEST = "/content/orchestration-course"

        if not os.path.isdir(DEST):
            subprocess.run(["git", "clone", "-q", REPO, DEST], check=True)
        os.chdir(DEST)

        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "-e", ".{extra}"],
            check=True,
        )
        os.environ.setdefault("COURSE_LANG", "en")  # change to ru or es
        """
    )


def _notebook(doc: str, setup: str, body: str) -> dict:
    badge = (
        f"[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)]"
        f"(https://colab.research.google.com/github/{GITHUB_REPO}/blob/main/notebooks/{{}})"
    )
    md = f"{doc}\n\n{badge}\n"
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
            "colab": {"provenance": []},
        },
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": md.splitlines(keepends=True)},
            {"cell_type": "code", "metadata": {}, "source": setup.splitlines(keepends=True), "outputs": [], "execution_count": None},
            {"cell_type": "code", "metadata": {}, "source": body.splitlines(keepends=True), "outputs": [], "execution_count": None},
        ],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in LABS:
        doc, body = _extract_body(spec["stem"])
        nb = _notebook(doc, _setup_cell(spec["sandbox"]), body)
        # Fix badge placeholder in markdown
        nb["cells"][0]["source"] = [
            line.replace("{{}}", f"{spec['stem']}.ipynb") for line in nb["cells"][0]["source"]
        ]
        out = OUT_DIR / f"{spec['stem']}.ipynb"
        out.write_text(json.dumps(nb, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {out}")


if __name__ == "__main__":
    main()
