"""courselib — teaching toolkit for the AI Agent Orchestration course.

Two layers, mirroring the course design:

- ``courselib.orchestration`` — neutral, dependency-free orchestration primitives
  (Tool, Agent, Router, Sequential, Parallel, handoff, Trace). You learn the
  *patterns* here, the same ones MCP / A2A / LangGraph / CrewAI implement.

- ``courselib.economy`` — a thin, sandbox-first wrapper over the real
  ``aimarket-agent`` SDK plus an embedded local hub + factory, so labs touch the
  *actual* AIMarket economy with zero infra and zero real money.
"""

from courselib.i18n import (
    Translator,
    available_languages,
    get_translator,
    resolve_lang,
)
from courselib.orchestration import (
    Agent,
    Handoff,
    Parallel,
    Router,
    Sequential,
    Tool,
    Trace,
)

__all__ = [
    "Agent",
    "Handoff",
    "Parallel",
    "Router",
    "Sequential",
    "Tool",
    "Trace",
    "Translator",
    "get_translator",
    "resolve_lang",
    "available_languages",
]

__version__ = "0.1.0"
