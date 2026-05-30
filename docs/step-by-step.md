# Step-by-step course guide

> **Audience:** developers learning multi-agent orchestration before (or alongside) AI-Factory.  
> **Languages:** `COURSE_LANG=en|ru|es` · UI strings in `i18n/` · this guide in English.  
> **Русский:** [step-by-step.ru.md](./step-by-step.ru.md) · **Español:** [step-by-step.es.md](./step-by-step.es.md)

---

## Table of contents

1. [Choose your track](#choose-your-track)
2. [Setup (10 minutes)](#setup-10-minutes)
3. [Module M1 — Agent loop & tool use](#module-m1--agent-loop--tool-use)
4. [Module M2 — Topologies](#module-m2--topologies)
5. [Module M3 — Handoffs & delegation](#module-m3--handoffs--delegation)
6. [Module M4 — Discovery & invocation](#module-m4--discovery--invocation)
7. [Module M8 — Economics of orchestration (advanced)](#module-m8--economics-of-orchestration-advanced)
8. [Modules M5–M7 — Concepts (labs coming)](#modules-m57--concepts-labs-coming)
9. [Module M9 — Observability in every lab](#module-m9--observability-in-every-lab)
10. [Bridge: from course to AI-Factory](#bridge-from-course-to-ai-factory)
11. [Self-check checklist](#self-check-checklist)
12. [Troubleshooting](#troubleshooting)

---

## Choose your track

| Track | Modules | Time | LLM | Hub |
|-------|---------|------|-----|-----|
| **Basic** | M1 → M2 → M3 → M4 | ~2 h | No | Sandbox only in M4 |
| **Advanced** | Basic + M8 | +1 h | Optional | Embedded sandbox hub |
| **Factory bridge** | After M4 or M8 | +30 min | Yes (your keys) | Real factory + Hub |

Read **M9** after each lab — every script prints a `Trace` you can inspect.

---

## Setup (10 minutes)

### Step 1 — Clone and install

```bash
git clone https://github.com/alexar76/orchestration-course.git
cd orchestration-course
pip install -e ".[dev]"
```

For economy labs (M4 sandbox, M8):

```bash
pip install -e ".[sandbox,dev]"
```

### Step 2 — Verify tests

```bash
pytest -q
```

**Expected:** all tests pass (i18n parity, orchestration primitives, economy helpers).

### Step 3 — Pick a language (optional)

```bash
export COURSE_LANG=ru   # or es, default en
python labs/lab01_agent_and_tool.py
```

### Step 4 — Colab alternative

1. Open [course site](https://alexar76.github.io/orchestration-course/) → **Open in Colab** on any lab.
2. Run the **setup cell** (clone + pip).
3. Set `os.environ["COURSE_LANG"] = "ru"` in setup if needed.
4. Run the lab cell.

---

## Module M1 — Agent loop & tool use

**Concept:** An agent is a policy that decides which tool to call.  
**Lab:** `labs/lab01_agent_and_tool.py` · **Time:** ~15 min · **Prerequisites:** setup done

### Steps

1. Open `labs/lab01_agent_and_tool.py` and read the module docstring (industry map: MCP, function calling).
2. Run locally:

   ```bash
   python labs/lab01_agent_and_tool.py
   ```

3. Watch the output for two tasks (translate / summarize). Each shows:
   - chosen **tool name**
   - **result** string
   - **trace** block at the end

4. Change `COURSE_LANG` and re-run — task text changes; tool mapping includes RU/ES keywords.

5. Open `courselib/orchestration.py` — find `Agent`, `Tool`, `Trace`, `keyword_policy` (5 min skim).

### Expected output (EN)

- Line `== Agent loop & tool use ==`
- Two task/result pairs
- Trace with `events` listing tool invocations

### Self-check

- [ ] You can explain: policy → tool → result → trace event
- [ ] You see why the lab uses **no LLM** (deterministic policy for teaching)

---

## Module M2 — Topologies

**Concept:** Sequential, parallel, and routing — shapes of multi-agent flows.  
**Lab:** `labs/lab02_topologies.py` · **Time:** ~20 min · **Prerequisites:** M1

### Steps

1. Run `python labs/lab02_topologies.py`.
2. Identify three sections in output: **sequential**, **parallel**, **router**.
3. For each topology, note how many agents ran and in what order (trace `events`).
4. Compare wall-clock: parallel block should show overlapping work (same parent span).
5. Edit the router keywords in the lab (optional) — add one route and re-run.

### Self-check

- [ ] Sequential = A then B
- [ ] Parallel = A and B without waiting for each other
- [ ] Router = one branch chosen by policy

---

## Module M3 — Handoffs & delegation

**Concept:** Transferring control to a specialist agent, bounded against loops.  
**Lab:** `labs/lab03_handoff.py` · **Time:** ~20 min · **Prerequisites:** M2

### Steps

1. Run `python labs/lab03_handoff.py`.
2. Find tasks that **delegate** to `legal` vs stay on `assistant`.
3. Read trace **handoffs** section — who handed off to whom.
4. Find the loop guard (max handoffs) in `courselib/orchestration.py` if curious.

### Self-check

- [ ] Delegation happens when policy returns `delegate:<agent>`
- [ ] Loop guard prevents infinite ping-pong

---

## Module M4 — Discovery & invocation

**Concept:** Finding and calling capabilities across a federated hub.  
**Lab:** `labs/lab04_discover_invoke.py` · **Time:** ~20 min · **Prerequisites:** `[hub-lite]` (~5 MB)

### Steps

1. Install: `pip install -e ".[hub-lite,dev]"`.
2. Run `python labs/lab04_discover_invoke.py` — hub-lite starts in ~2 s.
3. Note output: **discover** → capability list → **invoke** → result + receipt nonce.
4. Cross-read: [hub-integration-guide.md](../../docs/hub-integration-guide.md) § discovery.

### Self-check

- [ ] Discovery returns capability metadata (id, price)
- [ ] Invoke returns a structured result + receipt

---

## Module M5 — State, memory, context

**Lab:** `labs/lab05_state_context.py` · **Time:** ~20 min · **Prerequisites:** M2

### Steps

1. Run `python labs/lab05_state_context.py`.
2. Watch the **Context** bag grow: `brief` → `plan` → `artifacts` → `summary`.
3. Read trace `context_stage` events — keys after each stage.
4. **Exercise:** extend the pipeline (see lab footer). Check: `python labs/run_exercises.py --module m5`.

---

## Module M6 — Guardrails & safety

**Lab:** `labs/lab06_guardrails.py` · **Time:** ~20 min

### Steps

1. Run `python labs/lab06_guardrails.py`.
2. Compare safe task vs injection attack — note `guardrail_block` in trace.
3. **Exercise:** add a guardrail blocking `SECRET`. Check: `python labs/run_exercises.py --module m6`.

---

## Module M7 — Trust, verification, provenance

**Lab:** `labs/lab07_receipt_verify.py` · **Time:** ~25 min · **Prerequisites:** `[hub-lite]`

### Steps

1. Run `python labs/lab07_receipt_verify.py`.
2. Valid receipt → `True`; tampered price → `False`.
3. Skim `courselib/trust.py` — HMAC signing (stdlib, same idea as production).
4. **Exercise:** `python labs/run_exercises.py --module m7`.

---

## Module M8 — Economics of orchestration (advanced)

**Concept:** Payment channels, escrow, revenue routing for paid calls.  
**Lab:** `labs/lab08_metered_economy.py` · **Time:** ~45 min · **Prerequisites:** `[sandbox]` (~50 MB, install once)

### Steps

1. Install once: `pip install -e ".[sandbox,dev]"` (Colab: reuse session if lab04/07 already ran).
2. Run `python labs/lab08_metered_economy.py`.
3. Follow output: channel → invoke(s) → **total spent** → receipt.
4. Read [ai-market-protocol-v1.md](../../docs/ai-market-protocol-v1.md) § HTTP 402 and channels.

### Self-check

- [ ] You can name: discover → pay → invoke → receipt
- [ ] Channel amortizes multiple calls vs per-call 402

---

## Optional LLM demo (Module M1)

Default labs stay **deterministic** for reproducible learning. To see the same tool-routing pattern with a real model:

```bash
export USE_LLM=1
export OPENAI_API_KEY=sk-...
python labs/lab01_agent_and_tool.py
```

The policy calls an OpenAI-compatible API (`LLM_BASE_URL`, `LLM_MODEL` optional).

---

## Exercises & certificate

After labs, run DIY checks:

```bash
python labs/run_exercises.py
python labs/run_exercises.py --certificate "Your Name" --lang ru
```

Opens `certificate.html` — print to PDF from the browser. Credential ID is derived from name + date.

---

## Module M9 — Observability in every lab

**Concept:** Tracing multi-agent runs so behaviour is inspectable.  
**Covered in:** every lab via `Trace` · **Time:** 5 min after each lab

### Steps (repeat after M1–M4, M8)

1. Scroll to **trace** section in lab output.
2. Count `events` — map each to a step you saw in stdout.
3. Compare M2 sequential vs parallel event ordering.
4. Production path: [observability-langsmith.md](../../docs/observability-langsmith.md) — factory OTel + LangSmith (not required for course).

### Self-check

- [ ] Trace is the lab’s “unit test log” for agent behaviour
- [ ] You can correlate one failed invoke to one trace event

---

## Bridge: from course to AI-Factory

**Goal:** Run the same *patterns* on the full factory pipeline (~30 min).

1. **Start factory** (from monorepo root):

   ```bash
   docker compose up -d app
   # → http://localhost:9080
   ```

2. **Guest landing** — homepage phrase box → get `prod-…` → `/product/{id}`.

3. **Admin path** — [USER_GUIDE.md](../../docs/USER_GUIDE.md) § “Your first 15 minutes”:
   - `/admin/login`
   - **New product** → submit idea
   - **Pipeline** → watch stage strip (real agents, not course stubs)

4. **Map course → factory**

   | Course | Factory |
   |--------|---------|
   | M1 tool loop | Developer + QA tool calls |
   | M2 topologies | Pipeline stage graph |
   | M3 handoffs | Agent handoff audit log |
   | M4 discover/invoke | Hub catalog + `/ai-market/v2/invoke` |
   | M8 economy | Hub channels + storefront checkout |
   | M9 trace | Pipeline telemetry + Live Monitor |

5. **List on Hub** — [ecosystem-architecture.md](../../docs/ecosystem-architecture.md) — product → capability → invoke.

---

## Self-check checklist

After the basic track you should be able to:

- [ ] Run all of lab01–lab04 locally and in Colab
- [ ] Explain sequential vs parallel vs router with trace evidence
- [ ] Describe discover → invoke without opening HTTP docs
- [ ] Read a `Trace` block and find the failing step
- [ ] Name where factory pipeline extends M1–M4 (optional bridge)

After the advanced track add:

- [ ] Run lab08 and explain channel + receipt
- [ ] Open `ai-market-protocol-v1.md` and find 402 flow

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: courselib` | Run from repo root; labs prepend parent to `sys.path` |
| M4/M8 hang on start | Wait for embedded hub; check port not in use |
| `[sandbox]` install fails | Need `git` + network for GitHub deps |
| Empty RU/ES strings | Set `COURSE_LANG`; check `i18n/ru.json` keys match `en.json` |
| pytest i18n failure | Add missing keys to all three JSON files |
| Colab old code | Re-run setup cell; pin `main` branch |

**Factory issues:** [FAQ.md](../../docs/FAQ.md)

---

## Regenerate site & notebooks

After editing labs or i18n:

```bash
python3 scripts/build_course_assets.py
```

Guides in `docs/` are hand-maintained — update EN first, then RU/ES mirrors.
