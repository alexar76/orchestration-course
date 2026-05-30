"""Make ``courselib`` importable when running the course test-suite in-place."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
