#!/usr/bin/env python3
"""Generate static GitHub Pages site from i18n catalogs and lab metadata."""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SITE_ASSETS = ROOT / "site_assets"
I18N_DIR = ROOT / "i18n"
LABS_DIR = ROOT / "labs"

GITHUB_REPO = "alexar76/orchestration-course"
GITHUB_PAGES = f"https://alexar76.github.io/orchestration-course/"

QUICKSTART_COMMANDS = [
    f"git clone https://github.com/{GITHUB_REPO}.git",
    "cd orchestration-course",
    'pip install -e ".[hub-lite,dev]"',
    "python labs/lab01_agent_and_tool.py",
    "python labs/run_exercises.py",
]

LABS = [
    {"stem": "lab01_agent_and_tool", "module": "m1", "track": "basic"},
    {"stem": "lab02_topologies", "module": "m2", "track": "basic"},
    {"stem": "lab03_handoff", "module": "m3", "track": "basic"},
    {"stem": "lab04_discover_invoke", "module": "m4", "track": "economy"},
    {"stem": "lab05_state_context", "module": "m5", "track": "basic"},
    {"stem": "lab06_guardrails", "module": "m6", "track": "basic"},
    {"stem": "lab07_receipt_verify", "module": "m7", "track": "economy"},
    {"stem": "lab08_metered_economy", "module": "m8", "track": "advanced"},
]

MODULE_ORDER = [f"m{i}" for i in range(1, 10)]


def _lab_docstring(stem: str) -> str:
    src = (LABS_DIR / f"{stem}.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    doc = ast.get_docstring(tree) or ""
    return doc.strip()


def _load_catalogs() -> dict[str, dict]:
    catalogs: dict[str, dict] = {}
    for path in sorted(I18N_DIR.glob("*.json")):
        catalogs[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return catalogs


def _colab_url(stem: str) -> str:
    nb = f"notebooks/{stem}.ipynb"
    return (
        "https://colab.research.google.com/github/"
        f"{GITHUB_REPO}/blob/main/{nb}"
    )


def _build_payload(catalogs: dict[str, dict]) -> dict:
    labs = []
    for spec in LABS:
        labs.append(
            {
                **spec,
                "notebook": f"{spec['stem']}.ipynb",
                "script": f"labs/{spec['stem']}.py",
                "docstring": _lab_docstring(spec["stem"]),
                "colab": _colab_url(spec["stem"]),
            }
        )
    return {
        "repo": GITHUB_REPO,
        "pagesUrl": GITHUB_PAGES,
        "languages": list(catalogs.keys()),
        "catalogs": catalogs,
        "modules": MODULE_ORDER,
        "labs": labs,
        "quickstartCommands": QUICKSTART_COMMANDS,
        "stats": {"modules": len(MODULE_ORDER), "labs": len(LABS), "languages": len(catalogs)},
    }


def _write_assets() -> None:
    css = textwrap.dedent(
        """\
        :root {
          --bg: #070b12;
          --surface: rgba(14, 20, 32, 0.88);
          --surface2: rgba(22, 30, 48, 0.95);
          --text: #eef2ff;
          --muted: #94a3b8;
          --accent: #67e8f9;
          --accent2: #c084fc;
          --accent3: #34d399;
          --border: rgba(148, 163, 184, 0.16);
          --border-strong: rgba(103, 232, 249, 0.28);
          --ok: #34d399;
          --radius: 16px;
          --shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
          --mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
          --sans: "Space Grotesk", "Inter", ui-sans-serif, system-ui, sans-serif;
        }
        * { box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body {
          margin: 0;
          color: var(--text);
          font-family: var(--sans);
          background:
            radial-gradient(900px 520px at 8% -8%, rgba(103, 232, 249, 0.14), transparent 58%),
            radial-gradient(760px 480px at 92% 4%, rgba(192, 132, 252, 0.12), transparent 55%),
            radial-gradient(600px 400px at 50% 110%, rgba(52, 211, 153, 0.06), transparent 60%),
            var(--bg);
          line-height: 1.6;
          min-height: 100vh;
        }
        body::before {
          content: "";
          position: fixed;
          inset: 0;
          pointer-events: none;
          opacity: 0.35;
          background-image:
            linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
          background-size: 48px 48px;
          mask-image: radial-gradient(circle at 50% 20%, black, transparent 78%);
        }
        a { color: var(--accent); text-decoration: none; transition: color 0.15s ease; }
        a:hover { color: #a5f3fc; text-decoration: none; }
        .wrap { position: relative; max-width: 1120px; margin: 0 auto; padding: 1.5rem 1.25rem 4.5rem; }
        header.hero {
          position: relative;
          overflow: hidden;
          padding: 2.25rem 2rem 2rem;
          border: 1px solid var(--border-strong);
          border-radius: calc(var(--radius) + 6px);
          background:
            linear-gradient(135deg, rgba(103,232,249,0.08), rgba(192,132,252,0.06) 48%, rgba(255,255,255,0.02)),
            var(--surface);
          box-shadow: var(--shadow);
          backdrop-filter: blur(12px);
        }
        header.hero::after {
          content: "";
          position: absolute;
          top: -40%;
          right: -8%;
          width: 320px;
          height: 320px;
          border-radius: 50%;
          background: radial-gradient(circle, rgba(103,232,249,0.18), transparent 68%);
          pointer-events: none;
        }
        .hero-top {
          display: flex;
          flex-wrap: wrap;
          align-items: flex-start;
          justify-content: space-between;
          gap: 1rem;
          margin-bottom: 0.75rem;
        }
        .eyebrow {
          display: inline-flex;
          align-items: center;
          gap: 0.45rem;
          color: var(--accent);
          letter-spacing: 0.06em;
          text-transform: uppercase;
          font-size: 0.72rem;
          font-weight: 700;
        }
        .eyebrow::before {
          content: "";
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: linear-gradient(135deg, var(--accent), var(--accent2));
          box-shadow: 0 0 12px rgba(103,232,249,0.65);
        }
        .hero-badge {
          font-size: 0.78rem;
          color: var(--muted);
          padding: 0.35rem 0.75rem;
          border: 1px solid var(--border);
          border-radius: 999px;
          background: rgba(255,255,255,0.03);
        }
        h1 {
          font-size: clamp(2rem, 4.8vw, 3.1rem);
          margin: 0.35rem 0 0.65rem;
          line-height: 1.08;
          letter-spacing: -0.03em;
          max-width: 14ch;
        }
        .tagline {
          color: var(--muted);
          font-size: clamp(1rem, 2.2vw, 1.15rem);
          max-width: 46ch;
          margin: 0;
        }
        .hero-stats {
          display: grid;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          gap: 0.75rem;
          margin: 1.75rem 0 0.25rem;
        }
        .stat {
          padding: 0.85rem 1rem;
          border-radius: 14px;
          border: 1px solid var(--border);
          background: rgba(255,255,255,0.03);
        }
        .stat strong {
          display: block;
          font-size: 1.45rem;
          line-height: 1.1;
          background: linear-gradient(135deg, var(--accent), var(--accent2));
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }
        .stat span { color: var(--muted); font-size: 0.82rem; }
        .toolbar {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          align-items: center;
          margin-top: 1.35rem;
        }
        .lang-switch {
          display: inline-flex;
          border: 1px solid var(--border);
          border-radius: 999px;
          overflow: hidden;
          background: rgba(0,0,0,0.22);
        }
        .lang-switch button {
          border: 0;
          background: transparent;
          color: var(--muted);
          padding: 0.48rem 0.95rem;
          cursor: pointer;
          font: inherit;
          font-size: 0.82rem;
          font-weight: 600;
          transition: background 0.15s ease, color 0.15s ease;
        }
        .lang-switch button.active {
          background: linear-gradient(135deg, rgba(103,232,249,0.18), rgba(192,132,252,0.14));
          color: var(--text);
        }
        .btn {
          display: inline-flex;
          align-items: center;
          gap: 0.45rem;
          padding: 0.58rem 1rem;
          border-radius: 999px;
          border: 1px solid var(--border);
          background: rgba(255,255,255,0.04);
          color: var(--text);
          font-weight: 600;
          font-size: 0.9rem;
          transition: transform 0.15s ease, border-color 0.15s ease, background 0.15s ease;
        }
        .btn:hover {
          transform: translateY(-1px);
          border-color: var(--border-strong);
          background: rgba(255,255,255,0.07);
        }
        .btn.primary {
          background: linear-gradient(135deg, rgba(103,232,249,0.22), rgba(192,132,252,0.18));
          border-color: rgba(103,232,249,0.35);
          box-shadow: 0 8px 28px rgba(103,232,249,0.12);
        }
        .page-nav {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin: 1.35rem 0 0.25rem;
          padding: 0;
          list-style: none;
        }
        .page-nav a {
          display: inline-flex;
          padding: 0.42rem 0.85rem;
          border-radius: 999px;
          border: 1px solid transparent;
          color: var(--muted);
          font-size: 0.86rem;
          font-weight: 600;
        }
        .page-nav a:hover {
          color: var(--text);
          border-color: var(--border);
          background: rgba(255,255,255,0.04);
        }
        section { margin-top: 2.75rem; scroll-margin-top: 1.25rem; }
        .section-head {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }
        .section-head::before {
          content: "";
          width: 4px;
          height: 1.35rem;
          border-radius: 999px;
          background: linear-gradient(180deg, var(--accent), var(--accent2));
        }
        h2 { font-size: 1.45rem; margin: 0; letter-spacing: -0.02em; }
        .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
        .card {
          border: 1px solid var(--border);
          border-radius: var(--radius);
          background: var(--surface);
          padding: 1.15rem 1.2rem;
          backdrop-filter: blur(8px);
          transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
        }
        .card:hover {
          transform: translateY(-2px);
          border-color: rgba(103,232,249,0.22);
          box-shadow: 0 14px 40px rgba(0,0,0,0.22);
        }
        .card h3 { margin: 0 0 0.35rem; font-size: 1.06rem; line-height: 1.25; }
        .meta { color: var(--muted); font-size: 0.86rem; margin-bottom: 0.65rem; }
        .pill {
          display: inline-block;
          font-size: 0.7rem;
          font-weight: 700;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          padding: 0.2rem 0.55rem;
          border-radius: 999px;
          border: 1px solid var(--border);
          color: var(--muted);
          margin-right: 0.35rem;
          margin-top: 0.35rem;
        }
        .pill.lab { color: var(--ok); border-color: rgba(52,211,153,0.35); background: rgba(52,211,153,0.08); }
        .pill.soon { opacity: 0.75; }
        .pill.done { color: var(--ok); border-color: rgba(52,211,153,0.45); background: rgba(52,211,153,0.1); }
        .pill.track-economy { color: #fcd34d; border-color: rgba(252,211,77,0.35); }
        .pill.track-advanced { color: #f472b6; border-color: rgba(244,114,182,0.35); }
        .actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.85rem; }
        .actions a { font-size: 0.88rem; font-weight: 600; }
        footer {
          margin-top: 3.5rem;
          padding-top: 1.5rem;
          border-top: 1px solid var(--border);
          color: var(--muted);
          font-size: 0.9rem;
        }
        code.inline {
          font-family: var(--mono);
          font-size: 0.84em;
          background: rgba(255,255,255,0.06);
          padding: 0.14rem 0.4rem;
          border-radius: 6px;
          border: 1px solid var(--border);
        }
        .quickstart-card { padding: 0; overflow: hidden; }
        .quickstart-intro { padding: 1.15rem 1.2rem 0.85rem; color: var(--muted); margin: 0; }
        .terminal {
          border-top: 1px solid var(--border);
          background: linear-gradient(180deg, rgba(0,0,0,0.35), rgba(0,0,0,0.18));
        }
        .terminal-bar {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 0.75rem;
          padding: 0.65rem 0.9rem;
          border-bottom: 1px solid var(--border);
          background: rgba(255,255,255,0.03);
        }
        .terminal-dots { display: inline-flex; gap: 0.35rem; }
        .terminal-dots span {
          width: 10px; height: 10px; border-radius: 50%;
          background: rgba(255,255,255,0.12);
        }
        .terminal-dots span:nth-child(1) { background: #fb7185; }
        .terminal-dots span:nth-child(2) { background: #fbbf24; }
        .terminal-dots span:nth-child(3) { background: #34d399; }
        .terminal-title {
          flex: 1;
          text-align: center;
          color: var(--muted);
          font-size: 0.78rem;
          font-family: var(--mono);
        }
        .terminal-copy {
          border: 1px solid var(--border);
          background: rgba(255,255,255,0.04);
          color: var(--text);
          border-radius: 999px;
          padding: 0.28rem 0.7rem;
          font-size: 0.74rem;
          font-weight: 600;
          cursor: pointer;
          font-family: var(--sans);
        }
        .terminal-copy:hover { border-color: var(--border-strong); }
        .terminal-body {
          margin: 0;
          padding: 1rem 1.1rem 1.15rem;
          overflow-x: auto;
          font-family: var(--mono);
          font-size: 0.82rem;
          line-height: 1.65;
          color: #dbeafe;
        }
        .terminal-line { display: block; white-space: pre; }
        .terminal-line .prompt { color: var(--accent3); user-select: none; }
        .terminal-line.cmd { color: #e2e8f0; }
        .progress-bar {
          height: 10px; border-radius: 999px; background: rgba(255,255,255,0.04);
          border: 1px solid var(--border); overflow: hidden; margin: 1rem 0 0.5rem;
        }
        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent3));
          transition: width 0.25s ease;
        }
        .progress-label { color: var(--muted); font-size: 0.9rem; margin: 0 0 1rem; }
        .cert-intro { margin-top: 0; color: var(--muted); }
        .cert-grid { display: grid; gap: 1.25rem; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); margin-bottom: 1.25rem; }
        .cert-grid h3 { margin: 0 0 0.5rem; font-size: 0.95rem; }
        .checklist { display: grid; gap: 0.45rem; }
        .check-row {
          display: flex; align-items: flex-start; gap: 0.55rem;
          font-size: 0.9rem; color: var(--text); cursor: pointer;
          padding: 0.35rem 0.45rem;
          border-radius: 10px;
          transition: background 0.15s ease;
        }
        .check-row:hover { background: rgba(255,255,255,0.04); }
        .check-row input { margin-top: 0.2rem; accent-color: var(--accent); }
        .cert-form { display: grid; gap: 0.65rem; max-width: 420px; margin-top: 0.5rem; }
        .cert-form label { font-size: 0.85rem; color: var(--muted); }
        .cert-form input {
          padding: 0.7rem 0.9rem; border-radius: 12px; border: 1px solid var(--border);
          background: var(--surface2); color: var(--text); font: inherit;
        }
        .cert-form input:focus {
          outline: none;
          border-color: var(--border-strong);
          box-shadow: 0 0 0 3px rgba(103,232,249,0.12);
        }
        .cert-form input.invalid { border-color: #f87171; }
        .cert-hint { color: var(--muted); font-size: 0.85rem; margin: 0; }
        .lab-doc {
          white-space: pre-wrap;
          margin: 0.5rem 0 0;
          color: var(--muted);
          font-size: 0.86rem;
          font-family: var(--mono);
          padding: 0.75rem 0.85rem;
          border-radius: 12px;
          border: 1px solid var(--border);
          background: rgba(0,0,0,0.18);
        }
        .run-local { margin: 0.75rem 0 0; color: var(--muted); font-size: 0.88rem; }
        button.btn { cursor: pointer; font: inherit; }
        button.btn:disabled { opacity: 0.45; cursor: not-allowed; transform: none; }
        @media (max-width: 720px) {
          header.hero { padding: 1.5rem 1.15rem; }
          .hero-stats { grid-template-columns: 1fr; }
          h1 { max-width: none; }
        }
        """
    )
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    for name in ("progress.js", "certificate.js", "app.js"):
        src = (SITE_ASSETS / name).read_text(encoding="utf-8")
        (SITE / "assets" / name).write_text(src, encoding="utf-8")
    (SITE / "assets" / "style.css").write_text(css, encoding="utf-8")


def _write_index() -> None:
    html = textwrap.dedent(
        """\
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8" />
          <meta name="viewport" content="width=device-width, initial-scale=1" />
          <title>AI Agent Orchestration</title>
          <meta name="description" content="Hands-on Python course on AI agent orchestration patterns and agent economy." />
          <link rel="preconnect" href="https://fonts.googleapis.com" />
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
          <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet" />
          <link rel="stylesheet" href="assets/style.css" />
        </head>
        <body>
          <div class="wrap">
            <header class="hero">
              <div class="hero-top">
                <div class="eyebrow">Python · EN / RU / ES</div>
                <div class="hero-badge" id="hero-badge"></div>
              </div>
              <h1 id="title">AI Agent Orchestration</h1>
              <p class="tagline" id="tagline"></p>
              <div class="hero-stats" id="hero-stats"></div>
              <div class="toolbar">
                <div class="lang-switch" id="lang-switch" aria-label="Language"></div>
                <a class="btn" id="cert-nav" href="#certificate">Certificate</a>
                <a class="btn primary" href="https://github.com/alexar76/orchestration-course">GitHub ↗</a>
              </div>
              <nav aria-label="Sections">
                <ul class="page-nav" id="page-nav"></ul>
              </nav>
            </header>

            <section id="quickstart">
              <div class="section-head"><h2 id="quickstart-heading"></h2></div>
              <div class="card quickstart-card" id="quickstart-panel"></div>
            </section>

            <section id="certificate">
              <div class="section-head"><h2 id="certificate-heading"></h2></div>
              <div class="card" id="certificate-panel"></div>
            </section>

            <section id="modules">
              <div class="section-head"><h2 id="modules-heading"></h2></div>
              <div class="grid" id="modules-grid"></div>
            </section>

            <section id="labs">
              <div class="section-head"><h2 id="labs-heading"></h2></div>
              <div class="grid" id="labs"></div>
            </section>

            <footer>
              <p id="footer-note"></p>
            </footer>
          </div>
          <script src="assets/progress.js"></script>
          <script src="assets/certificate.js"></script>
          <script src="assets/app.js"></script>
        </body>
        </html>
        """
    )
    (SITE / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    catalogs = _load_catalogs()
    payload = _build_payload(catalogs)
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "data" / "course.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _write_assets()
    _write_index()
    print(f"Wrote {SITE}/")


if __name__ == "__main__":
    main()
