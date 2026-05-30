#!/usr/bin/env bash
# Push course-app to alexar76/orchestration-course (create the empty repo on GitHub first).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REMOTE="${COURSE_REMOTE:-https://github.com/alexar76/orchestration-course.git}"
BRANCH="${COURSE_BRANCH:-main}"

python3 scripts/build_course_assets.py

if [[ ! -d .git ]]; then
  git init -b "$BRANCH"
fi

git add -A
if git diff --cached --quiet; then
  echo "Nothing to commit."
else
  git commit -m "$(cat <<'EOF'
Publish AI Agent Orchestration course.

GitHub Pages landing, Colab notebooks, EN/RU/ES i18n, and runnable labs.
EOF
)"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "$REMOTE"
git push -u origin "$BRANCH"
echo "OK → $REMOTE"
