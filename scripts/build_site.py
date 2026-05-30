#!/usr/bin/env python3
"""Generate static GitHub Pages site from i18n catalogs and lab metadata."""

from __future__ import annotations

import ast
import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
I18N_DIR = ROOT / "i18n"
LABS_DIR = ROOT / "labs"

GITHUB_REPO = "alexar76/orchestration-course"
GITHUB_PAGES = f"https://alexar76.github.io/orchestration-course/"

LABS = [
    {"stem": "lab01_agent_and_tool", "module": "m1", "track": "basic"},
    {"stem": "lab02_topologies", "module": "m2", "track": "basic"},
    {"stem": "lab03_handoff", "module": "m3", "track": "basic"},
    {"stem": "lab04_discover_invoke", "module": "m4", "track": "economy"},
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
    }


def _write_assets() -> None:
    css = textwrap.dedent(
        """\
        :root {
          --bg: #0b0f17;
          --surface: #121826;
          --surface2: #1a2233;
          --text: #e8edf7;
          --muted: #93a0b8;
          --accent: #6ee7ff;
          --accent2: #a78bfa;
          --border: #243049;
          --ok: #34d399;
          --radius: 14px;
          --shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
          font-family: "Inter", ui-sans-serif, system-ui, -apple-system, sans-serif;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          color: var(--text);
          background:
            radial-gradient(1200px 600px at 10% -10%, rgba(110, 231, 255, 0.12), transparent 60%),
            radial-gradient(900px 500px at 90% 0%, rgba(167, 139, 250, 0.12), transparent 55%),
            var(--bg);
          line-height: 1.55;
        }
        a { color: var(--accent); text-decoration: none; }
        a:hover { text-decoration: underline; }
        .wrap { max-width: 1080px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }
        header.hero {
          padding: 2.5rem;
          border: 1px solid var(--border);
          border-radius: calc(var(--radius) + 4px);
          background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
          box-shadow: var(--shadow);
        }
        .eyebrow {
          color: var(--accent);
          letter-spacing: 0.08em;
          text-transform: uppercase;
          font-size: 0.78rem;
          font-weight: 700;
        }
        h1 { font-size: clamp(1.9rem, 4vw, 2.8rem); margin: 0.4rem 0 0.6rem; line-height: 1.15; }
        .tagline { color: var(--muted); font-size: 1.08rem; max-width: 52ch; }
        .toolbar {
          display: flex;
          flex-wrap: wrap;
          gap: 0.75rem;
          align-items: center;
          margin-top: 1.5rem;
        }
        .lang-switch { display: inline-flex; border: 1px solid var(--border); border-radius: 999px; overflow: hidden; }
        .lang-switch button {
          border: 0;
          background: transparent;
          color: var(--muted);
          padding: 0.45rem 0.9rem;
          cursor: pointer;
          font: inherit;
        }
        .lang-switch button.active { background: var(--surface2); color: var(--text); }
        .btn {
          display: inline-flex;
          align-items: center;
          gap: 0.4rem;
          padding: 0.55rem 0.95rem;
          border-radius: 999px;
          border: 1px solid var(--border);
          background: var(--surface2);
          color: var(--text);
          font-weight: 600;
        }
        .btn.primary { background: linear-gradient(135deg, rgba(110,231,255,0.18), rgba(167,139,250,0.18)); border-color: rgba(110,231,255,0.35); }
        section { margin-top: 2.25rem; }
        h2 { font-size: 1.35rem; margin: 0 0 1rem; }
        .grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
        .card {
          border: 1px solid var(--border);
          border-radius: var(--radius);
          background: var(--surface);
          padding: 1.1rem 1.15rem;
        }
        .card h3 { margin: 0 0 0.35rem; font-size: 1.05rem; }
        .meta { color: var(--muted); font-size: 0.88rem; margin-bottom: 0.65rem; }
        .pill {
          display: inline-block;
          font-size: 0.72rem;
          font-weight: 700;
          letter-spacing: 0.04em;
          text-transform: uppercase;
          padding: 0.18rem 0.5rem;
          border-radius: 999px;
          border: 1px solid var(--border);
          color: var(--muted);
          margin-right: 0.35rem;
        }
        .pill.lab { color: var(--ok); border-color: rgba(52,211,153,0.35); }
        .pill.soon { opacity: 0.75; }
        .actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.75rem; }
        .actions a { font-size: 0.88rem; }
        footer { margin-top: 3rem; color: var(--muted); font-size: 0.9rem; }
        code.inline {
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: 0.85em;
          background: rgba(255,255,255,0.05);
          padding: 0.12rem 0.35rem;
          border-radius: 6px;
        }
        """
    )
    js = textwrap.dedent(
        """\
        (function () {
          const state = { lang: "en", data: null };

          function t(key) {
            const cat = state.data.catalogs[state.lang] || state.data.catalogs.en;
            const parts = key.split(".");
            let node = cat;
            for (const p of parts) {
              if (!node || typeof node !== "object" || !(p in node)) return key;
              node = node[p];
            }
            return typeof node === "string" ? node : key;
          }

          function labForModule(mod) {
            return state.data.labs.find((l) => l.module === mod);
          }

          function renderModules() {
            const grid = document.getElementById("modules");
            grid.innerHTML = "";
            for (const mod of state.data.modules) {
              const info = (state.data.catalogs[state.lang].modules || {})[mod] || {};
              const lab = labForModule(mod);
              const card = document.createElement("article");
              card.className = "card";
              const title = info.title || mod;
              const concept = info.concept || "";
              const industry = info.industry || "";
              let pills = `<span class="pill">${mod.toUpperCase()}</span>`;
              let actions = "";
              if (lab) {
                pills += `<span class="pill lab">${t("site.has_lab")}</span>`;
                if (lab.track === "advanced") pills += `<span class="pill">${t("site.advanced")}</span>`;
                actions = `
                  <div class="actions">
                    <a class="btn primary" href="${lab.colab}" target="_blank" rel="noopener">${t("site.open_colab")}</a>
                    <a href="https://github.com/${state.data.repo}/blob/main/${lab.script}">${t("site.view_source")}</a>
                  </div>`;
              } else {
                pills += `<span class="pill soon">${t("site.coming_soon")}</span>`;
              }
              card.innerHTML = `
                <h3>${title}</h3>
                <div class="meta">${industry}</div>
                <p>${concept}</p>
                ${pills}
                ${actions}`;
              grid.appendChild(card);
            }
          }

          function renderLabs() {
            const list = document.getElementById("labs");
            list.innerHTML = "";
            for (const lab of state.data.labs) {
              const mod = lab.module.toUpperCase();
              const modInfo = (state.data.catalogs[state.lang].modules || {})[lab.module] || {};
              const item = document.createElement("article");
              item.className = "card";
              item.innerHTML = `
                <h3>${modInfo.title || lab.stem}</h3>
                <div class="meta">${t("site.module")} ${mod} · ${lab.track}</div>
                <pre style="white-space:pre-wrap;margin:0;color:var(--muted);font-size:0.86rem;font-family:inherit;">${lab.docstring.replace(/</g, "&lt;")}</pre>
                <div class="actions">
                  <a class="btn primary" href="${lab.colab}" target="_blank" rel="noopener">${t("site.open_colab")}</a>
                  <a href="https://github.com/${state.data.repo}/blob/main/${lab.script}">${t("site.view_source")}</a>
                </div>
                <p style="margin:0.75rem 0 0;color:var(--muted);font-size:0.88rem;">
                  ${t("site.run_local")}: <code class="inline">python ${lab.script}</code>
                </p>`;
              list.appendChild(item);
            }
          }

          function renderHero() {
            const c = state.data.catalogs[state.lang].course || {};
            document.getElementById("title").textContent = c.title || "AI Agent Orchestration";
            document.getElementById("tagline").textContent = c.tagline || "";
            document.getElementById("modules-heading").textContent = t("site.modules_heading");
            document.getElementById("labs-heading").textContent = t("site.labs_heading");
            document.getElementById("quickstart-heading").textContent = t("site.quickstart_heading");
            document.getElementById("quickstart-body").innerHTML = t("site.quickstart_body");
            document.getElementById("footer-note").textContent = t("site.footer");
          }

          function setLang(lang) {
            state.lang = lang;
            document.querySelectorAll(".lang-switch button").forEach((btn) => {
              btn.classList.toggle("active", btn.dataset.lang === lang);
            });
            renderHero();
            renderModules();
            renderLabs();
          }

          fetch("data/course.json")
            .then((r) => r.json())
            .then((data) => {
              state.data = data;
              const switcher = document.getElementById("lang-switch");
              for (const lang of data.languages) {
                const btn = document.createElement("button");
                btn.type = "button";
                btn.dataset.lang = lang;
                btn.textContent = lang.toUpperCase();
                btn.addEventListener("click", () => setLang(lang));
                switcher.appendChild(btn);
              }
              setLang("en");
            });
        })();
        """
    )
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "style.css").write_text(css, encoding="utf-8")
    (SITE / "assets" / "app.js").write_text(js, encoding="utf-8")


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
          <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
          <link rel="stylesheet" href="assets/style.css" />
        </head>
        <body>
          <div class="wrap">
            <header class="hero">
              <div class="eyebrow">Python · EN / RU / ES</div>
              <h1 id="title">AI Agent Orchestration</h1>
              <p class="tagline" id="tagline"></p>
              <div class="toolbar">
                <div class="lang-switch" id="lang-switch" aria-label="Language"></div>
                <a class="btn primary" href="https://github.com/alexar76/orchestration-course">GitHub</a>
              </div>
            </header>

            <section>
              <h2 id="quickstart-heading"></h2>
              <div class="card" id="quickstart-body"></div>
            </section>

            <section>
              <h2 id="modules-heading"></h2>
              <div class="grid" id="modules"></div>
            </section>

            <section>
              <h2 id="labs-heading"></h2>
              <div class="grid" id="labs"></div>
            </section>

            <footer>
              <p id="footer-note"></p>
            </footer>
          </div>
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
