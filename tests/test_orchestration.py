"""Tests for the neutral orchestration primitives (offline, deterministic)."""

import pytest

from courselib.orchestration import (
    Agent,
    Handoff,
    Parallel,
    Router,
    Sequential,
    Tool,
    Trace,
)
from courselib.orchestration import keyword_policy


def test_tool_is_callable():
    t = Tool("upper", lambda s: s.upper(), "uppercases")
    assert t("hi") == "HI"


def test_agent_keyword_policy_calls_tool():
    trace = Trace()
    agent = Agent(
        "translator",
        policy=keyword_policy({"translate": "translate"}),
        tools=[Tool("translate", lambda s: f"translated: {s}")],
        trace=trace,
    )
    assert agent.run("please translate this") == "translated: please translate this"
    assert trace.of_kind("tool_call")[0]["tool"] == "translate"


def test_handoff_delegates_to_another_agent():
    trace = Trace()
    legal = Agent("legal", policy=keyword_policy({"contract": "review"}),
                  tools=[Tool("review", lambda s: "reviewed")], trace=trace)

    def front_policy(task, agent):
        return Handoff(to=legal, task=task, reason="needs legal")

    front = Agent("front", policy=front_policy, trace=trace)
    assert front.run("check this contract") == "reviewed"
    assert trace.of_kind("handoff")[0]["to"] == "legal"


def test_handoff_loop_is_bounded():
    trace = Trace()
    a = Agent("a", trace=trace)
    b = Agent("b", trace=trace)
    a.policy = lambda task, agent: Handoff(to=b, task=task)
    b.policy = lambda task, agent: Handoff(to=a, task=task)
    with pytest.raises(RuntimeError):
        a.run("loop", max_handoffs=3)


def test_router_picks_by_predicate():
    t = Trace()
    es = Agent("es", policy=keyword_policy({"hola": "greet"}),
               tools=[Tool("greet", lambda s: "¡hola!")])
    en = Agent("en", policy=keyword_policy({"hello": "greet"}),
               tools=[Tool("greet", lambda s: "hello!")])
    router = Router(
        routes=[(lambda x: "hola" in x.lower(), es), (lambda x: "hello" in x.lower(), en)],
        trace=t,
    )
    assert router.run("hola amigo") == "¡hola!"
    assert router.run("hello there") == "hello!"
    assert t.of_kind("route")


def test_sequential_threads_output():
    pipe = Sequential([lambda x: x + 1, lambda x: x * 10, lambda x: x - 5])
    assert pipe.run(1) == 15  # ((1+1)*10)-5


def test_parallel_gathers():
    par = Parallel([lambda x: x + 1, lambda x: x * 2, lambda x: x ** 2])
    assert par.run(3) == [4, 6, 9]
