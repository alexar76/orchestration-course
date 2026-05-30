"""Optional LLM-backed policy (stdlib HTTP, no extra pip deps).

Set ``USE_LLM=1`` and ``OPENAI_API_KEY`` (or ``LLM_API_KEY``) to swap the
deterministic keyword brain for a real model in lab demos.

Compatible with OpenAI and most OpenAI-compatible gateways via env vars:
``LLM_BASE_URL`` (default https://api.openai.com/v1),
``LLM_MODEL`` (default gpt-4o-mini).
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Optional

from courselib.orchestration import Agent, Policy, Tool


def llm_enabled() -> bool:
    return os.environ.get("USE_LLM", "").strip().lower() in ("1", "true", "yes", "on")


def _api_key() -> Optional[str]:
    return os.environ.get("OPENAI_API_KEY") or os.environ.get("LLM_API_KEY")


def _chat(messages: list[dict[str, str]]) -> str:
    key = _api_key()
    if not key:
        raise RuntimeError("USE_LLM=1 but OPENAI_API_KEY / LLM_API_KEY is not set")
    base = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    body = json.dumps({"model": model, "messages": messages, "temperature": 0}).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        raise RuntimeError(f"LLM HTTP {e.code}: {detail}") from e
    return data["choices"][0]["message"]["content"].strip()


def llm_tool_picker(tools: dict[str, Tool], task: str) -> Optional[str]:
    """Ask the model which tool name to use, or None if no tool fits."""
    listing = "\n".join(f"- {name}: {t.description or name}" for name, t in tools.items())
    prompt = (
        "You are a tool router. Reply with ONLY the exact tool name to use, "
        "or the word NONE if no tool fits.\n\n"
        f"Tools:\n{listing}\n\nTask: {task}\n\nTool:"
    )
    answer = _chat([{"role": "user", "content": prompt}]).strip().strip('"').strip("'")
    if answer.upper() == "NONE":
        return None
    if answer in tools:
        return answer
    low = answer.lower()
    for name in tools:
        if name.lower() == low:
            return name
    return None


def llm_policy(fallback_routes: Optional[dict[str, str]] = None) -> Policy:
    """Build a policy that uses an LLM when enabled, else keyword fallback."""

    def policy(task: str, agent: Agent) -> Any:
        if llm_enabled() and agent.tools:
            agent.trace.emit("llm_route", agent=agent.name, task=task)
            pick = llm_tool_picker(agent.tools, task)
            if pick:
                tool = agent.tools[pick]
                agent.trace.emit("tool_call", agent=agent.name, tool=pick, task=task, via="llm")
                return tool(task)
            agent.trace.emit("llm_no_tool", agent=agent.name, task=task)
            return f"[{agent.name}] LLM: no tool matched"
        if fallback_routes:
            from courselib.orchestration import keyword_policy
            return keyword_policy(fallback_routes)(task, agent)
        return f"[{agent.name}] {task}"

    return policy
