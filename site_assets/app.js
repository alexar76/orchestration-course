(function () {
  const EXERCISE_MODS = ["m1", "m2", "m3", "m5", "m6", "m7"];
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

  function labStems() {
    return state.data.labs.map((l) => l.stem);
  }

  function renderCertificatePanel() {
    const panel = document.getElementById("certificate-panel");
    if (!panel) return;
    const sum = CourseProgress.summary(labStems(), EXERCISE_MODS);
    const total = sum.labsTotal + sum.exTotal;
    const done = sum.labsDone + sum.exDone;
    const pct = total ? Math.round((done / total) * 100) : 0;

    let labRows = "";
    for (const lab of state.data.labs) {
      const modInfo = state.data.catalogs[state.lang].modules[lab.module] || {};
      const checked = CourseProgress.isLabDone(lab.stem) ? "checked" : "";
      labRows += `
        <label class="check-row">
          <input type="checkbox" data-lab="${lab.stem}" ${checked} />
          <span>${modInfo.title || lab.stem}</span>
        </label>`;
    }

    let exRows = "";
    for (const mod of EXERCISE_MODS) {
      const modInfo = state.data.catalogs[state.lang].modules[mod] || {};
      const checked = CourseProgress.isExerciseDone(mod) ? "checked" : "";
      exRows += `
        <label class="check-row">
          <input type="checkbox" data-exercise="${mod}" ${checked} />
          <span>${mod.toUpperCase()} · ${modInfo.title || mod}</span>
        </label>`;
    }

    const canIssue = sum.complete;
    panel.innerHTML = `
      <p class="cert-intro">${t("site.certificate_intro")}</p>
      <div class="progress-bar" aria-hidden="true"><div class="progress-fill" style="width:${pct}%"></div></div>
      <p class="progress-label">${t("site.certificate_progress")}: ${done}/${total} (${pct}%)</p>
      <div class="cert-grid">
        <div>
          <h3>${t("site.certificate_labs")}</h3>
          <div class="checklist">${labRows}</div>
        </div>
        <div>
          <h3>${t("site.certificate_exercises")}</h3>
          <div class="checklist">${exRows}</div>
        </div>
      </div>
      <div class="cert-form">
        <label for="cert-name">${t("site.certificate_name_label")}</label>
        <input id="cert-name" type="text" placeholder="${t("site.certificate_name_placeholder")}" maxlength="80" />
        <button type="button" id="cert-btn" class="btn primary" ${canIssue ? "" : "disabled"}>
          ${t("site.certificate_generate")}
        </button>
        ${canIssue ? "" : `<p class="cert-hint">${t("site.certificate_locked")}</p>`}
      </div>`;

    panel.querySelectorAll("[data-lab]").forEach((el) => {
      el.addEventListener("change", () => {
        CourseProgress.setLabDone(el.dataset.lab, el.checked);
        renderCertificatePanel();
        renderLabs();
      });
    });
    panel.querySelectorAll("[data-exercise]").forEach((el) => {
      el.addEventListener("change", () => {
        CourseProgress.setExerciseDone(el.dataset.exercise, el.checked);
        renderCertificatePanel();
      });
    });

    const btn = panel.querySelector("#cert-btn");
    const nameInput = panel.querySelector("#cert-name");
    if (btn) {
      btn.addEventListener("click", async () => {
        const name = (nameInput.value || "").trim();
        if (!name) {
          nameInput.focus();
          nameInput.classList.add("invalid");
          return;
        }
        if (!CourseProgress.summary(labStems(), EXERCISE_MODS).complete) return;
        await CourseCertificate.open(name, state.lang, state.data.catalogs[state.lang]);
      });
    }
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
        const done = CourseProgress.isLabDone(lab.stem);
        pills += `<span class="pill lab">${t("site.has_lab")}</span>`;
        if (done) pills += `<span class="pill done">${t("site.certificate_mark_done")}</span>`;
        if (lab.track === "advanced") pills += `<span class="pill">${t("site.advanced")}</span>`;
        actions = `
          <div class="actions">
            <a class="btn primary" href="${lab.colab}" target="_blank" rel="noopener">${t("site.open_colab")}</a>
            <a href="https://github.com/${state.data.repo}/blob/main/${lab.script}">${t("site.view_source")}</a>
            <button type="button" class="btn mark-lab" data-stem="${lab.stem}">${done ? t("site.certificate_mark_done") : t("site.certificate_mark_lab")}</button>
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
    grid.querySelectorAll(".mark-lab").forEach((btn) => {
      btn.addEventListener("click", () => {
        const stem = btn.dataset.stem;
        CourseProgress.setLabDone(stem, !CourseProgress.isLabDone(stem));
        renderModules();
        renderLabs();
        renderCertificatePanel();
      });
    });
  }

  function renderLabs() {
    const list = document.getElementById("labs");
    list.innerHTML = "";
    for (const lab of state.data.labs) {
      const mod = lab.module.toUpperCase();
      const modInfo = (state.data.catalogs[state.lang].modules || {})[lab.module] || {};
      const done = CourseProgress.isLabDone(lab.stem);
      const item = document.createElement("article");
      item.className = "card";
      item.innerHTML = `
        <h3>${modInfo.title || lab.stem} ${done ? '<span class="pill done">' + t("site.certificate_mark_done") + "</span>" : ""}</h3>
        <div class="meta">${t("site.module")} ${mod} · ${lab.track}</div>
        <pre class="lab-doc">${lab.docstring.replace(/</g, "&lt;")}</pre>
        <div class="actions">
          <a class="btn primary" href="${lab.colab}" target="_blank" rel="noopener">${t("site.open_colab")}</a>
          <a href="https://github.com/${state.data.repo}/blob/main/${lab.script}">${t("site.view_source")}</a>
          <button type="button" class="btn mark-lab" data-stem="${lab.stem}">${done ? t("site.certificate_mark_done") : t("site.certificate_mark_lab")}</button>
        </div>
        <p class="run-local">${t("site.run_local")}: <code class="inline">python ${lab.script}</code></p>`;
      list.appendChild(item);
    }
    list.querySelectorAll(".mark-lab").forEach((btn) => {
      btn.addEventListener("click", () => {
        const stem = btn.dataset.stem;
        CourseProgress.setLabDone(stem, !CourseProgress.isLabDone(stem));
        renderModules();
        renderLabs();
        renderCertificatePanel();
      });
    });
  }

  function renderHero() {
    const c = state.data.catalogs[state.lang].course || {};
    document.getElementById("title").textContent = c.title || "AI Agent Orchestration";
    document.getElementById("tagline").textContent = c.tagline || "";
    document.getElementById("modules-heading").textContent = t("site.modules_heading");
    document.getElementById("labs-heading").textContent = t("site.labs_heading");
    document.getElementById("quickstart-heading").textContent = t("site.quickstart_heading");
    document.getElementById("quickstart-body").innerHTML = t("site.quickstart_body");
    document.getElementById("certificate-heading").textContent = t("site.certificate_heading");
    const certNav = document.getElementById("cert-nav");
    if (certNav) certNav.textContent = t("site.certificate_nav");
    document.getElementById("footer-note").textContent = t("site.footer");
  }

  function setLang(lang) {
    state.lang = lang;
    localStorage.setItem("course-lang", lang);
    document.documentElement.lang = lang;
    document.querySelectorAll(".lang-switch button").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.lang === lang);
    });
    renderHero();
    renderCertificatePanel();
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
      setLang(localStorage.getItem("course-lang") || "en");
    });
})();
