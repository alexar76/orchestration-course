"""Neutral, dependency-free orchestration primitives.

These exist to teach the *patterns* of agent orchestration with fully
deterministic, inspectable code — no LLM, no network — so every lab is
reproducible and testable. Each primitive maps to a course module:

    Tool        M1  tool use
    Agent       M1  the agent loop
    Router      M2  routing topology
    Sequential  M2  sequential pipeline
    Parallel    M2  parallel fan-out
    Handoff     M3  delegation / control transfer
    Trace           M9  observability
    Context         M5  threaded state / bill of materials
    StatefulPipeline M5  pipeline with shared context bag
    Guardrail       M6  pre/post safety checks

The same shapes appear in MCP (tools), A2A (handoffs/agent cards),
LangGraph (graphs) and CrewAI (crews) — the course maps each one across.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional


# ── Observability (M9) ───────────────────────────────────────────────────────

@dataclass
class Trace:
    """Append-only event log so orchestration is inspectable, not magic."""

    events: list[dict[str, Any]] = field(default_factory=list)

    def emit(self, kind: str, **data: Any) -> None:
        self.events.append({"t": round(time.time(), 6), "kind": kind, **data})

    def of_kind(self, kind: str) -> list[dict[str, Any]]:
        return [e for e in self.events if e["kind"] == kind]

    def __len__(self) -> int:
        return len(self.events)


# ── Tools & handoffs ─────────────────────────────────────────────────────────

@dataclass
class Tool:
    """A named capability an agent can call (M1)."""

    name: str
    fn: Callable[..., Any]
    description: str = ""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


@dataclass
class Handoff:
    """An agent's decision to delegate the task to another agent (M3)."""

    to: "Agent"
    task: str
    reason: str = ""


# A policy maps (task, agent) → an action. Returning a Handoff delegates;
# returning anything else is treated as the agent's final answer.
Policy = Callable[[str, "Agent"], Any]


def keyword_policy(routes: dict[str, str]) -> Policy:
    """Build a deterministic policy that calls a tool when a keyword matches.

    ``routes`` maps a keyword → tool name. First match wins. Useful for labs
    where you want predictable behaviour instead of an LLM.
    """

    def policy(task: str, agent: "Agent") -> Any:
        low = task.lower()
        for keyword, tool_name in routes.items():
            if keyword in low:
                tool = agent.tools.get(tool_name)
                if tool is None:
                    raise KeyError(f"{agent.name}: policy references unknown tool {tool_name!r}")
                agent.trace.emit("tool_call", agent=agent.name, tool=tool_name, task=task)
                return tool(task)
        agent.trace.emit("no_route", agent=agent.name, task=task)
        return f"[{agent.name}] no tool matched: {task}"

    return policy


# ── Agent (M1) ───────────────────────────────────────────────────────────────

class Agent:
    """A minimal agent: a name, some tools, and a policy that decides actions.

    The policy is the agent's "brain" — swap in a keyword router for tests, or
    wire it to an LLM in a real build. Handoffs are resolved by the orchestrator
    that runs the agent (see Router/Sequential), bounded to prevent loops.
    """

    def __init__(
        self,
        name: str,
        policy: Optional[Policy] = None,
        tools: Optional[list[Tool]] = None,
        trace: Optional[Trace] = None,
    ):
        self.name = name
        self.tools: dict[str, Tool] = {t.name: t for t in (tools or [])}
        self.policy: Policy = policy or (lambda task, agent: f"[{name}] {task}")
        self.trace = trace if trace is not None else Trace()

    def add_tool(self, tool: Tool) -> "Agent":
        self.tools[tool.name] = tool
        return self

    def step(self, task: str) -> Any:
        """One decision. May return a Handoff (delegation) or a final result."""
        self.trace.emit("agent_step", agent=self.name, task=task)
        return self.policy(task, self)

    def run(self, task: str, max_handoffs: int = 5) -> Any:
        """Run to completion, following handoffs up to ``max_handoffs`` (M3)."""
        current: Agent = self
        current_task = task
        for _ in range(max_handoffs + 1):
            out = current.step(current_task)
            if isinstance(out, Handoff):
                self.trace.emit(
                    "handoff", frm=current.name, to=out.to.name,
                    reason=out.reason, task=out.task,
                )
                out.to.trace = self.trace  # share the trace across the chain
                current, current_task = out.to, out.task
                continue
            return out
        raise RuntimeError(f"handoff limit ({max_handoffs}) exceeded — possible delegation loop")


# ── Topologies (M2) ──────────────────────────────────────────────────────────

class Router:
    """Pick one agent for a task by predicate, then run it (M2: routing)."""

    def __init__(self, routes: list[tuple[Callable[[str], bool], Agent]], default: Optional[Agent] = None,
                 trace: Optional[Trace] = None):
        self.routes = routes
        self.default = default
        self.trace = trace if trace is not None else Trace()

    def run(self, task: str) -> Any:
        for predicate, agent in self.routes:
            if predicate(task):
                self.trace.emit("route", to=agent.name, task=task)
                agent.trace = self.trace
                return agent.run(task)
        if self.default is None:
            raise ValueError(f"no route for task: {task!r}")
        self.trace.emit("route_default", to=self.default.name, task=task)
        self.default.trace = self.trace
        return self.default.run(task)


Step = Callable[[Any], Any]


class Sequential:
    """Run steps in order, threading each output into the next (M2: pipeline)."""

    def __init__(self, steps: list[Step], trace: Optional[Trace] = None):
        self.steps = steps
        self.trace = trace if trace is not None else Trace()

    def run(self, value: Any) -> Any:
        out = value
        for i, step in enumerate(self.steps):
            self.trace.emit("pipeline_stage", index=i, input=out)
            out = step(out)
        self.trace.emit("pipeline_done", output=out)
        return out


class Parallel:
    """Fan a task out to several steps and gather results (M2: parallel)."""

    def __init__(self, steps: list[Step], trace: Optional[Trace] = None):
        self.steps = steps
        self.trace = trace if trace is not None else Trace()

    def run(self, value: Any) -> list[Any]:
        results = []
        for i, step in enumerate(self.steps):
            self.trace.emit("fanout", index=i)
            results.append(step(value))
        self.trace.emit("gather", count=len(results))
        return results


# ── State & context (M5) ─────────────────────────────────────────────────────

@dataclass
class Context:
    """Mutable state bag threaded through pipeline stages (M5).

    Think of ``data`` as a lightweight bill of materials: each stage reads and
    writes keys instead of passing opaque strings only.
    """

    data: dict[str, Any] = field(default_factory=dict)
    trace: Optional[Trace] = None

    def set(self, key: str, value: Any) -> "Context":
        self.data[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


ContextStep = Callable[[Context], Context]


class StatefulPipeline:
    """Pipeline where every stage receives the same ``Context`` (M5)."""

    def __init__(self, steps: list[ContextStep], trace: Optional[Trace] = None):
        self.steps = steps
        self.trace = trace if trace is not None else Trace()

    def run(self, initial: Optional[dict[str, Any]] = None) -> Context:
        ctx = Context(data=dict(initial or {}), trace=self.trace)
        for i, step in enumerate(self.steps):
            self.trace.emit("context_stage", index=i, keys=sorted(ctx.data.keys()))
            ctx.trace = self.trace
            ctx = step(ctx)
        self.trace.emit("context_done", keys=sorted(ctx.data.keys()))
        return ctx


# ── Guardrails (M6) ──────────────────────────────────────────────────────────

GuardrailFn = Callable[[str, str], Optional[str]]


@dataclass
class Guardrail:
    """Named pre/post check. Return an error string to block, or ``None`` to pass."""

    name: str
    check: GuardrailFn

    def run(self, text: str, phase: str) -> Optional[str]:
        return self.check(text, phase)


def injection_guardrail() -> Guardrail:
    """Block common prompt-injection phrases (deterministic demo guardrail)."""

    needles = (
        "ignore previous", "ignore all", "system prompt", "jailbreak",
        "игнорируй предыдущ", "ignora instrucciones",
    )

    def check(text: str, phase: str) -> Optional[str]:
        low = text.lower()
        for n in needles:
            if n in low:
                return f"{phase}: injection pattern {n!r}"
        return None

    return Guardrail("injection_filter", check)


def length_guardrail(max_len: int = 500) -> Guardrail:
    def check(text: str, phase: str) -> Optional[str]:
        if len(text) > max_len:
            return f"{phase}: output too long ({len(text)} > {max_len})"
        return None

    return Guardrail("max_length", check)


def guarded_tool(tool: Tool, guardrails: list[Guardrail], trace: Trace) -> Tool:
    """Wrap a tool with pre/post guardrails (M6)."""

    def fn(task: str) -> Any:
        for g in guardrails:
            err = g.run(task, "pre")
            if err:
                trace.emit("guardrail_block", guardrail=g.name, phase="pre", reason=err, tool=tool.name)
                return f"[blocked:{g.name}] {err}"
        trace.emit("tool_call", agent="guarded", tool=tool.name, task=task)
        result = tool(task)
        for g in guardrails:
            err = g.run(str(result), "post")
            if err:
                trace.emit("guardrail_block", guardrail=g.name, phase="post", reason=err, tool=tool.name)
                return f"[blocked:{g.name}] {err}"
        return result

    return Tool(tool.name, fn, tool.description)
