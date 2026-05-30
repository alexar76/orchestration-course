"""Course completion certificate (HTML, print-ready)."""

from __future__ import annotations

import hashlib
import html
from datetime import date
from pathlib import Path
from typing import Iterable

from courselib.exercises import EXERCISES, all_passed, run_all
from courselib.i18n import get_translator

COMPLETED_MODULES = ("m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9")


def certificate_id(name: str, issued: date | None = None) -> str:
    issued = issued or date.today()
    digest = hashlib.sha256(f"{name.strip().lower()}|{issued.isoformat()}".encode()).hexdigest()
    return digest[:12].upper()


def _module_badges(modules: Iterable[str], t) -> str:
    pills = []
    for mod in modules:
        title = t(f"modules.{mod}.title")
        pills.append(f'<span class="pill">{html.escape(mod.upper())} · {html.escape(title)}</span>')
    return "\n".join(pills)


def render_html(
    name: str,
    *,
    lang: str = "en",
    issued: date | None = None,
    modules: Iterable[str] | None = None,
) -> str:
    issued = issued or date.today()
    modules = tuple(modules or COMPLETED_MODULES)
    t = get_translator(lang)
    cid = certificate_id(name, issued)
    course_title = t("course.title")
    tagline = t("course.tagline")
    display_name = html.escape(name.strip())
    badges = _module_badges(modules, t)

    labels = {
        "en": ("Certificate of Completion", "Awarded to", "Date", "Credential ID", "Modules mastered"),
        "ru": ("Сертификат об окончании", "Награждается", "Дата", "ID сертификата", "Освоенные модули"),
        "es": ("Certificado de finalización", "Otorgado a", "Fecha", "ID del certificado", "Módulos completados"),
    }
    L = labels.get(lang, labels["en"])

    return f"""<!DOCTYPE html>
<html lang="{html.escape(lang)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(L[0])} — {display_name}</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap');
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: radial-gradient(1200px 600px at 20% 0%, #1a2744 0%, #0b0f17 55%, #06080d 100%);
      font-family: Inter, system-ui, sans-serif; color: #e8edf7;
    }}
    .cert {{
      width: min(920px, 94vw); padding: 3rem 3.5rem 2.5rem;
      border: 1px solid rgba(120, 160, 255, 0.25);
      border-radius: 24px;
      background: linear-gradient(145deg, rgba(18,24,38,0.95), rgba(10,14,22,0.98));
      box-shadow: 0 30px 80px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
      position: relative; overflow: hidden;
    }}
    .cert::before {{
      content: ""; position: absolute; inset: 0;
      background: radial-gradient(circle at 85% 15%, rgba(99,140,255,0.18), transparent 45%);
      pointer-events: none;
    }}
    .eyebrow {{ letter-spacing: 0.22em; text-transform: uppercase; font-size: 0.72rem; color: #8fa3cc; }}
    h1 {{
      font-family: "Playfair Display", Georgia, serif; font-size: clamp(2rem, 4vw, 2.8rem);
      margin: 0.4rem 0 0.2rem; background: linear-gradient(90deg, #fff, #b8c9ff);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .course {{ color: #9fb0d0; margin-bottom: 2rem; }}
    .label {{ font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.14em; color: #7d91b8; }}
    .name {{
      font-size: clamp(1.8rem, 3.5vw, 2.4rem); font-weight: 700; margin: 0.35rem 0 1.6rem;
      border-bottom: 1px solid rgba(120,160,255,0.25); padding-bottom: 0.75rem;
    }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 2rem; margin-bottom: 1.5rem; color: #c5d2ea; }}
    .meta div {{ min-width: 140px; }}
    .meta strong {{ display: block; font-size: 1.05rem; color: #fff; margin-top: 0.25rem; }}
    .modules {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }}
    .pill {{
      font-size: 0.78rem; padding: 0.35rem 0.65rem; border-radius: 999px;
      background: rgba(80,120,255,0.12); border: 1px solid rgba(120,160,255,0.22);
    }}
    .footer {{
      margin-top: 2rem; display: flex; justify-content: space-between; align-items: end;
      gap: 1rem; flex-wrap: wrap; color: #7d91b8; font-size: 0.85rem;
    }}
    .seal {{
      width: 72px; height: 72px; border-radius: 50%;
      border: 2px solid rgba(120,160,255,0.35);
      display: grid; place-items: center; font-weight: 700; color: #a8bbff;
      background: radial-gradient(circle at 30% 30%, rgba(120,160,255,0.2), transparent);
    }}
    @media print {{
      body {{ background: #fff; color: #111; }}
      .cert {{ box-shadow: none; border-color: #ccc; background: #fff; color: #111; }}
      h1, .name, .meta strong {{ -webkit-text-fill-color: initial; color: #111; }}
    }}
  </style>
</head>
<body>
  <article class="cert">
    <div class="eyebrow">{html.escape(L[0])}</div>
    <h1>{html.escape(course_title)}</h1>
    <p class="course">{html.escape(tagline)}</p>
    <div class="label">{html.escape(L[1])}</div>
    <div class="name">{display_name}</div>
    <div class="meta">
      <div><span class="label">{html.escape(L[2])}</span><strong>{issued.isoformat()}</strong></div>
      <div><span class="label">{html.escape(L[3])}</span><strong>{cid}</strong></div>
    </div>
    <div class="label">{html.escape(L[4])}</div>
    <div class="modules">{badges}</div>
    <div class="footer">
      <div>AIMarket · AI Agent Orchestration · open course</div>
      <div class="seal" aria-hidden="true">AI</div>
    </div>
  </article>
</body>
</html>
"""


def write_certificate(path: Path, name: str, *, lang: str = "en", require_exercises: bool = True) -> Path:
    if require_exercises and not all_passed():
        results = run_all()
        failed = [k for k, v in results.items() if v != "ok"]
        raise RuntimeError(f"Exercises not passed: {', '.join(failed)}. Run: python labs/run_exercises.py")
    html_doc = render_html(name, lang=lang)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html_doc, encoding="utf-8")
    return path
