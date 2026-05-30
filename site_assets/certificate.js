/** Client-side certificate document (matches courselib/certificate.py design). */
window.CourseCertificate = (function () {
  const LABELS = {
    en: ["Certificate of Completion", "Awarded to", "Date", "Credential ID", "Modules mastered"],
    ru: ["Сертификат об окончании", "Награждается", "Дата", "ID сертификата", "Освоенные модули"],
    es: ["Certificado de finalización", "Otorgado a", "Fecha", "ID del certificado", "Módulos completados"],
  };

  function esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function credentialId(name, issued) {
    const raw = name.trim().toLowerCase() + "|" + issued;
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(raw));
    return Array.from(new Uint8Array(buf))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("")
      .slice(0, 12)
      .toUpperCase();
  }

  async function buildHtml(name, lang, catalog) {
    const L = LABELS[lang] || LABELS.en;
    const issued = new Date().toISOString().slice(0, 10);
    const cid = await credentialId(name, issued);
    const courseTitle = catalog.course?.title || "AI Agent Orchestration";
    const tagline = catalog.course?.tagline || "";
    const modules = catalog.modules || {};
    const modKeys = Object.keys(modules).sort();
    const badges = modKeys
      .map((mod) => {
        const title = modules[mod]?.title || mod;
        return `<span class="pill">${esc(mod.toUpperCase())} · ${esc(title)}</span>`;
      })
      .join("\n");

    return `<!DOCTYPE html>
<html lang="${esc(lang)}">
<head>
  <meta charset="utf-8" />
  <title>${esc(L[0])} — ${esc(name)}</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:wght@700&display=swap" rel="stylesheet" />
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: radial-gradient(1200px 600px at 20% 0%, #1a2744 0%, #0b0f17 55%, #06080d 100%);
      font-family: Inter, system-ui, sans-serif; color: #e8edf7; }
    .cert { width: min(920px, 94vw); padding: 3rem 3.5rem 2.5rem;
      border: 1px solid rgba(120,160,255,0.25); border-radius: 24px;
      background: linear-gradient(145deg, rgba(18,24,38,0.95), rgba(10,14,22,0.98));
      box-shadow: 0 30px 80px rgba(0,0,0,0.45); position: relative; overflow: hidden; }
    .cert::before { content:""; position:absolute; inset:0;
      background: radial-gradient(circle at 85% 15%, rgba(99,140,255,0.18), transparent 45%); pointer-events:none; }
    .eyebrow { letter-spacing: 0.22em; text-transform: uppercase; font-size: 0.72rem; color: #8fa3cc; }
    h1 { font-family: "Playfair Display", Georgia, serif; font-size: clamp(2rem, 4vw, 2.8rem); margin: 0.4rem 0 0.2rem;
      background: linear-gradient(90deg, #fff, #b8c9ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .course { color: #9fb0d0; margin-bottom: 2rem; }
    .label { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.14em; color: #7d91b8; }
    .name { font-size: clamp(1.8rem, 3.5vw, 2.4rem); font-weight: 700; margin: 0.35rem 0 1.6rem;
      border-bottom: 1px solid rgba(120,160,255,0.25); padding-bottom: 0.75rem; }
    .meta { display: flex; flex-wrap: wrap; gap: 2rem; margin-bottom: 1.5rem; color: #c5d2ea; }
    .meta strong { display: block; font-size: 1.05rem; color: #fff; margin-top: 0.25rem; }
    .modules { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; }
    .pill { font-size: 0.78rem; padding: 0.35rem 0.65rem; border-radius: 999px;
      background: rgba(80,120,255,0.12); border: 1px solid rgba(120,160,255,0.22); }
    .footer { margin-top: 2rem; display: flex; justify-content: space-between; align-items: end; color: #7d91b8; font-size: 0.85rem; }
    .seal { width: 72px; height: 72px; border-radius: 50%; border: 2px solid rgba(120,160,255,0.35);
      display: grid; place-items: center; font-weight: 700; color: #a8bbff; }
    .print-bar { position: fixed; top: 1rem; right: 1rem; }
    .print-bar button { padding: 0.6rem 1rem; border-radius: 999px; border: 0; cursor: pointer;
      background: #6ee7ff; color: #0b0f17; font-weight: 700; }
    @media print { .print-bar { display: none; } body { background: #fff; color: #111; }
      .cert { box-shadow: none; background: #fff; color: #111; }
      h1, .name, .meta strong { -webkit-text-fill-color: initial; color: #111; } }
  </style>
</head>
<body>
  <div class="print-bar"><button onclick="window.print()">${esc(L[0])} · Print</button></div>
  <article class="cert">
    <div class="eyebrow">${esc(L[0])}</div>
    <h1>${esc(courseTitle)}</h1>
    <p class="course">${esc(tagline)}</p>
    <div class="label">${esc(L[1])}</div>
    <div class="name">${esc(name.trim())}</div>
    <div class="meta">
      <div><span class="label">${esc(L[2])}</span><strong>${issued}</strong></div>
      <div><span class="label">${esc(L[3])}</span><strong>${cid}</strong></div>
    </div>
    <div class="label">${esc(L[4])}</div>
    <div class="modules">${badges}</div>
    <div class="footer">
      <div>AIMarket · AI Agent Orchestration · open course</div>
      <div class="seal" aria-hidden="true">AI</div>
    </div>
  </article>
</body>
</html>`;
  }

  async function open(name, lang, catalog) {
    const html = await buildHtml(name, lang, catalog);
    const win = window.open("", "_blank");
    if (!win) {
      alert("Allow pop-ups to open your certificate.");
      return;
    }
    win.document.write(html);
    win.document.close();
  }

  return { open };
})();
