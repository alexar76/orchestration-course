#!/usr/bin/env python3
"""Patch published aimarket-hub until satellite sync includes _is_safe_path."""

from __future__ import annotations

import sys
from pathlib import Path

SNIPPET = '''
_SAFE_ID_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.@")


def _is_safe_path(segment: str) -> bool:
    """Reject path traversal in product/capability ids used in upstream URLs."""
    if not segment or len(segment) > 80:
        return False
    if ".." in segment or "/" in segment or "\\\\" in segment:
        return False
    return all(c in _SAFE_ID_CHARS for c in segment)
'''


def main() -> None:
    hub_root = Path(sys.argv[1] if len(sys.argv) > 1 else "aimarket-hub")
    api = hub_root / "aimarket_hub" / "api.py"
    text = api.read_text(encoding="utf-8")
    if "def _is_safe_path" in text:
        print(f"OK: {api} already patched")
        return
    needle = "logger = logging.getLogger(__name__)\n"
    if needle not in text:
        raise SystemExit(f"cannot patch {api}: anchor not found")
    api.write_text(text.replace(needle, needle + SNIPPET + "\n", 1), encoding="utf-8")
    print(f"Patched {api}")


if __name__ == "__main__":
    main()
