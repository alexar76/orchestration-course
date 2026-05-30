<!-- aicom-mirror-notice -->
> **Mirror — read-only.**
> The canonical source for `course` lives in the AI-Factory monorepo.
> Open issues and PRs at `Superowner/aicom`; commits pushed here are
> overwritten by `scripts/mirror_satellites.sh` on the next sync run.
> See `docs/repository-canonical-policy.md` for the policy.

# AI Agent Orchestration

**Learn the patterns. Run them against a real agent economy.**

Interactive Python course: 9 modules (M1–M9), runnable labs, full **EN / RU / ES** localization.

| | |
| --- | --- |
| **Course site** | [alexar76.github.io/orchestration-course](https://alexar76.github.io/orchestration-course/) |
| **Colab** | Open any lab from the site — notebooks live in [`notebooks/`](notebooks/) |
| **Languages** | `COURSE_LANG=en` · `ru` · `es` |

## Modules

| Module | Topic | Lab |
| --- | --- | --- |
| M1 | Agent loop & tool use | [`lab01`](labs/lab01_agent_and_tool.py) |
| M2 | Topologies (sequential, parallel, router) | [`lab02`](labs/lab02_topologies.py) |
| M3 | Handoffs & delegation | [`lab03`](labs/lab03_handoff.py) |
| M4 | Discovery & invocation | [`lab04`](labs/lab04_discover_invoke.py) |
| M5–M7 | State, guardrails, trust | concepts (labs coming) |
| M8 | Economics of orchestration | [`lab08`](labs/lab08_metered_economy.py) |
| M9 | Observability | covered via `Trace` in every lab |

**Basic track:** labs 1–4 — deterministic patterns, no LLM.  
**Advanced track:** lab 8 — real `aimarket-agent` SDK, embedded sandbox hub, signed receipts.

## Quick start (local)

```bash
git clone https://github.com/alexar76/orchestration-course.git
cd orchestration-course
pip install -e ".[sandbox,dev]"
pytest -q
python labs/lab01_agent_and_tool.py
COURSE_LANG=ru python labs/lab01_agent_and_tool.py
```

Economy labs (4, 8) need the `[sandbox]` extra — it pulls `uvicorn`, `httpx`, and the AIMarket SDK + hub from GitHub.

## Google Colab

Each lab has a notebook under `notebooks/` with a one-cell setup (clone + pip install). Example:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/alexar76/orchestration-course/blob/main/notebooks/lab01_agent_and_tool.ipynb)

Set `COURSE_LANG` in the setup cell to `ru` or `es` before running the lab cell.

## Project layout

```
courselib/     # Neutral orchestration primitives + economy sandbox bridge
labs/          # Runnable lab scripts
notebooks/     # Colab-ready .ipynb (generated — run scripts/build_course_assets.py)
i18n/          # en / ru / es JSON catalogs
tests/         # pytest suite
site/          # GitHub Pages static output (built in CI)
```

## Regenerate site & notebooks

```bash
python3 scripts/build_course_assets.py
```

## Source of truth

Developed inside the [aicom](https://github.com/alexar76/aicom) monorepo at `course-app/`, mirrored to this repository.

## License

MIT — see [LICENSE](LICENSE).
