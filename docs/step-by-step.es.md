# Guía paso a paso del curso

> **Audiencia:** desarrolladores que aprenden orquestación multi-agente antes o junto con AI-Factory.  
> **Idioma de labs:** `COURSE_LANG=en|ru|es` · UI en `i18n/` · esta guía en español.  
> **English:** [step-by-step.md](./step-by-step.md) · **Русский:** [step-by-step.ru.md](./step-by-step.ru.md)

---

## Índice

1. [Elige tu track](#elige-tu-track)
2. [Instalación (10 min)](#instalación-10-min)
3. [M1 — Bucle del agente y herramientas](#m1--bucle-del-agente-y-herramientas)
4. [M2 — Topologías](#m2--topologías)
5. [M3 — Handoffs y delegación](#m3--handoffs-y-delegación)
6. [M4 — Discovery e invocación](#m4--discovery-e-invocación)
7. [M8 — Economía de la orquestación (avanzado)](#m8--economía-de-la-orquestación-avanzado)
8. [M5–M7 — Conceptos (labs próximamente)](#m5m7--conceptos-labs-próximamente)
9. [M9 — Observabilidad en cada lab](#m9--observabilidad-en-cada-lab)
10. [Puente: del curso a AI-Factory](#puente-del-curso-a-ai-factory)
11. [Lista de autocomprobación](#lista-de-autocomprobación)
12. [Problemas frecuentes](#problemas-frecuentes)

---

## Elige tu track

| Track | Módulos | Tiempo | LLM | Hub |
|-------|---------|--------|-----|-----|
| **Básico** | M1 → M4 | ~2 h | No | Sandbox solo en M4 |
| **Avanzado** | Básico + M8 | +1 h | Opcional | Hub sandbox embebido |
| **Puente Factory** | Tras M4 o M8 | +30 min | Sí (tus keys) | Factory + Hub real |

Tras **cada** lab revisa el bloque **Trace** (M9).

---

## Instalación (10 min)

```bash
git clone https://github.com/alexar76/orchestration-course.git
cd orchestration-course
pip install -e ".[dev]"
# M4 y M8:
pip install -e ".[sandbox,dev]"
pytest -q
export COURSE_LANG=es
python labs/lab01_agent_and_tool.py
```

**Colab:** [sitio del curso](https://alexar76.github.io/orchestration-course/) → Open in Colab → celda setup → `COURSE_LANG=es`.

---

## M1 — Bucle del agente y herramientas

**Lab:** `lab01_agent_and_tool.py` · **~15 min**

### Pasos

1. Lee el docstring del lab.
2. `python labs/lab01_agent_and_tool.py`
3. Observa: tarea → herramienta → resultado → **trace**.
4. Re-ejecuta con `COURSE_LANG=es`.
5. Revisa `courselib/orchestration.py` (`Agent`, `Tool`, `Trace`).

### Autocomprobación

- [ ] Explicas policy → tool → result → trace
- [ ] Entiendes por qué no hay LLM (determinismo pedagógico)

---

## M2 — Topologías

**Lab:** `lab02_topologies.py` · **~20 min**

1. Ejecuta el lab.
2. Identifica **sequential**, **parallel**, **router** en la salida.
3. Compara eventos en trace.

---

## M3 — Handoffs y delegación

**Lab:** `lab03_handoff.py` · **~20 min**

1. Ejecuta el lab.
2. Busca delegación a `legal` vs `assistant`.
3. Sección **handoffs** en trace.

---

## M4 — Discovery e invocación

**Lab:** `lab04_discover_invoke.py` · **~30 min** · requiere `[sandbox]`

1. `pip install -e ".[sandbox,dev]"`
2. Ejecuta el lab (espera ~10 s al arrancar hub).
3. discover → invoke → resultado.
4. Lectura: [hub-integration-guide.md](../../docs/hub-integration-guide.md)

---

## M8 — Economía de la orquestación (avanzado)

**Lab:** `lab08_metered_economy.py` · **~45 min**

1. Ejecuta el lab.
2. channel → invoke → **total spent** → receipt.
3. Lee [ai-market-protocol-v1.md](../../docs/ai-market-protocol-v1.md) (402, channels).

---

## M5–M7 — Conceptos (labs próximamente)

| Módulo | Acción |
|--------|--------|
| M5 State | `i18n/es.json` → `modules.m5`; Factory Pipeline artifacts |
| M6 Guardrails | `modules.m6`; plugin aimarket-safety |
| M7 Provenance | `modules.m7`; receipts tras M8 |

Ver [agents.md](../../docs/agents.md)

---

## M9 — Observabilidad en cada lab

Tras cada lab (5 min):

1. Bloque **trace** al final
2. Mapea `events` a pasos en stdout
3. Producción: [observability-langsmith.md](../../docs/observability-langsmith.md)

---

## Puente: del curso a AI-Factory

1. `docker compose up -d app` → http://localhost:9080
2. Landing invitado en `/`
3. [USER_GUIDE.es.md](../../docs/USER_GUIDE.es.md) — primeros 15 minutos en Admin
4. Tabla curso → Factory (igual que guía EN): M1 tools → Developer; M4 → Hub invoke; M8 → channels.

---

## Lista de autocomprobación

- [ ] labs 01–04 local y Colab
- [ ] sequential / parallel / router con trace
- [ ] discover → invoke explicado
- [ ] (Avanzado) lab08 + receipt

---

## Problemas frecuentes

| Problema | Solución |
|----------|----------|
| `No module courselib` | Ejecutar desde raíz del repo |
| M4/M8 cuelga | Esperar hub; revisar puerto |
| pip `[sandbox]` falla | git + red |
| RU/ES vacío | `COURSE_LANG` |
| pytest i18n | claves en en/ru/es.json |

Factory: [FAQ.es.md](../../docs/FAQ.es.md)

```bash
python3 scripts/build_course_assets.py
```

Guías en `docs/` — mantenimiento manual; EN primero, luego RU/ES.
