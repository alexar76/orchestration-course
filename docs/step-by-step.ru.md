# Пошаговое руководство по курсу

> **Для кого:** разработчики, изучающие оркестрацию агентов до (или параллельно с) AI-Factory.  
> **Язык лаб:** `COURSE_LANG=ru|en|es` · строки UI в `i18n/` · этот гайд на русском.  
> **English:** [step-by-step.md](./step-by-step.md) · **Español:** [step-by-step.es.md](./step-by-step.es.md)

---

## Содержание

1. [Выбор трека](#выбор-трека)
2. [Установка (10 минут)](#установка-10-минут)
3. [M1 — Цикл агента и инструменты](#m1--цикл-агента-и-инструменты)
4. [M2 — Топологии](#m2--топологии)
5. [M3 — Передача управления (handoff)](#m3--передача-управления-handoff)
6. [M4 — Discovery и invoke](#m4--discovery-и-invoke)
7. [M8 — Экономика оркестрации (продвинутый)](#m8--экономика-оркестрации-продвинутый)
8. [M5 — State и context](#m5--state-и-context)
9. [M6 — Guardrails](#m6--guardrails)
10. [M7 — Trust и receipts](#m7--trust-и-receipts)
11. [M8 — Экономика (продвинутый)](#m8--экономика-оркестрации-продвинутый)
12. [LLM (опционально)](#llm-опционально)
13. [Упражнения и сертификат](#упражнения-и-сертификат)
14. [M9 — Наблюдаемость](#m9--наблюдаемость-в-каждой-лабе)
10. [Мост: от курса к AI-Factory](#мост-от-курса-к-ai-factory)
11. [Чеклист самопроверки](#чеклист-самопроверки)
12. [Типичные проблемы](#типичные-проблемы)

---

## Выбор трека

| Трек | Модули | Время | LLM | Hub |
|------|--------|-------|-----|-----|
| **Базовый** | M1 → M4 | ~2 ч | Нет | Sandbox только в M4 |
| **Продвинутый** | Базовый + M8 | +1 ч | Опционально | Встроенный sandbox hub |
| **Мост к Factory** | После M4 или M8 | +30 мин | Да (ваши ключи) | Реальная фабрика + Hub |

После **каждой** лабы смотрите блок **Trace** (M9).

---

## Установка (10 минут)

### Шаг 1 — Клон и установка

```bash
git clone https://github.com/alexar76/orchestration-course.git
cd orchestration-course
pip install -e ".[dev]"
```

Для M4 и M8:

```bash
pip install -e ".[sandbox,dev]"
```

### Шаг 2 — Тесты

```bash
pytest -q
```

### Шаг 3 — Язык интерфейса лаб

```bash
export COURSE_LANG=ru
python labs/lab01_agent_and_tool.py
```

### Шаг 4 — Google Colab

1. Откройте [сайт курса](https://alexar76.github.io/orchestration-course/) → **Open in Colab**.
2. Выполните setup-ячейку (clone + pip).
3. В setup: `os.environ["COURSE_LANG"] = "ru"`.
4. Запустите ячейку лабы.

---

## M1 — Цикл агента и инструменты

**Концепция:** агент — политика выбора инструмента.  
**Лаба:** `labs/lab01_agent_and_tool.py` · **~15 мин**

### Шаги

1. Прочитайте docstring в начале файла лабы.
2. `python labs/lab01_agent_and_tool.py`
3. Найдите в выводе: задача → инструмент → результат → **trace**.
4. Перезапустите с `COURSE_LANG=ru` — текст задач меняется, ключевые слова для policy тоже.
5. Откройте `courselib/orchestration.py` — классы `Agent`, `Tool`, `Trace`.

### Самопроверка

- [ ] Объясняете цепочку: policy → tool → result → trace
- [ ] Понимаете, зачем без LLM (детерминизм для обучения)

---

## M2 — Топологии

**Лаба:** `lab02_topologies.py` · **~20 мин** · нужен M1

### Шаги

1. `python labs/lab02_topologies.py`
2. Три блока: **sequential**, **parallel**, **router**
3. Сравните порядок событий в trace
4. (Опционально) добавьте ключевое слово в router и перезапустите

### Самопроверка

- [ ] Sequential — по очереди; parallel — параллельно; router — одна ветка

---

## M3 — Передача управления (handoff)

**Лаба:** `lab03_handoff.py` · **~20 мин**

### Шаги

1. `python labs/lab03_handoff.py`
2. Найдите делегирование на `legal` vs работу `assistant`
3. Секция **handoffs** в trace

---

## M4 — Discovery и invoke

**Лаба:** `lab04_discover_invoke.py` · **~20 мин** · нужен `[hub-lite]` (~5 MB)

### Шаги

1. `pip install -e ".[hub-lite,dev]"`
2. `python labs/lab04_discover_invoke.py` (hub-lite ~2 с)
3. discover → invoke → receipt nonce

---

## M5 — State и context

**Лаба:** `lab05_state_context.py` · **~20 мин**

1. `python labs/lab05_state_context.py`
2. Смотрите рост Context: brief → plan → artifacts
3. Упражнение: `python labs/run_exercises.py --module m5`

---

## M6 — Guardrails

**Лаба:** `lab06_guardrails.py` · **~20 мин**

1. `python labs/lab06_guardrails.py`
2. Сравните safe vs injection — `guardrail_block` в trace
3. Упражнение: `python labs/run_exercises.py --module m6`

---

## M7 — Trust и receipts

**Лаба:** `lab07_receipt_verify.py` · **~25 мин** · `[hub-lite]`

1. `python labs/lab07_receipt_verify.py`
2. Валидный чек → True; подделка → False
3. Упражнение: `python labs/run_exercises.py --module m7`

---

## M8 — Экономика оркестрации (продвинутый)

**Лаба:** `lab08_metered_economy.py` · **~45 мин** · `[sandbox]` (~50 MB, один раз)

### Шаги

1. `pip install -e ".[sandbox,dev]"` (в Colab — один раз на сессию)
2. `python labs/lab08_metered_economy.py`
3. channel → **total spent** → receipt

---

## LLM (опционально)

```bash
USE_LLM=1 OPENAI_API_KEY=sk-… python labs/lab01_agent_and_tool.py
```

---

## Упражнения и сертификат

```bash
python labs/run_exercises.py
python labs/run_exercises.py --certificate "Иван Петров" --lang ru
```

HTML-сертификат → Print → PDF в браузере.

---

## M9 — Наблюдаемость в каждой лабе

После каждой лабы (5 мин):

1. Блок **trace** в конце stdout
2. Сопоставьте `events` с шагами
3. Production: [observability-langsmith.md](../../docs/observability-langsmith.md)

---

## Мост: от курса к AI-Factory

**~30 мин**

1. `docker compose up -d app` → http://localhost:9080
2. Гостевой лендинг на `/` → `prod-…`
3. [USER_GUIDE.ru.md](../../docs/USER_GUIDE.ru.md) — «Первые 15 минут»: Admin → New product → Pipeline
4. Сопоставление:

   | Курс | Factory |
   |------|---------|
   | M1 tools | Developer + QA |
   | M2 топологии | Граф pipeline |
   | M3 handoff | Agent handoff audit |
   | M4 invoke | Hub `/ai-market/v2/invoke` |
   | M8 economy | Channels + checkout |

---

## Чеклист самопроверки

Базовый трек:

- [ ] lab01–lab07 локально
- [ ] `python labs/run_exercises.py` — все ✓
- [ ] Сертификат: `--certificate "Имя" --lang ru`

Продвинутый:

- [ ] lab08 + channel + receipt

---

## Типичные проблемы

| Проблема | Решение |
|----------|---------|
| `No module courselib` | Запуск из корня репозитория |
| M4/M8 зависает | Подождите hub; проверьте порт |
| Ошибка `[sandbox]` pip | Нужны git и сеть |
| Пустой RU | `export COURSE_LANG=ru` |
| pytest i18n | Ключи во всех трёх JSON |

Factory: [FAQ.ru.md](../../docs/FAQ.ru.md)

---

Обновление сайта после правок лаб:

```bash
python3 scripts/build_course_assets.py
```

Гайды в `docs/` правятся вручную — сначала EN, затем RU/ES.
