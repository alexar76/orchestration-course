"""Lab 01 - The agent loop & tool use (Module 1).

Concept: an agent is a policy that decides which tool to call.
Industry map: MCP exposes tools to a model; here we make the decision
deterministic so you can see the loop with no LLM in the way.

Optional LLM: set USE_LLM=1 and OPENAI_API_KEY to see the same pattern with a real model.

Run:  python labs/lab01_agent_and_tool.py
      COURSE_LANG=ru python labs/lab01_agent_and_tool.py
Exercise: python labs/run_exercises.py --module m1
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.i18n import get_translator
from courselib.llm import llm_enabled
from courselib.orchestration import Agent, Tool, Trace, keyword_policy


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m1.title')} ==")

    routes = {
        "translate": "translate", "summarize": "summarize",
        "переведи": "translate", "выжимк": "summarize",
        "traduce": "translate", "resume": "summarize",
    }
    trace = Trace()

    if llm_enabled():
        from courselib.llm import llm_policy
        policy = llm_policy(fallback_routes=routes)
        print(t("labs.lab01.llm_on"))
    else:
        policy = keyword_policy(routes)
        print(t("labs.lab01.llm_off"))

    agent = Agent(
        name="assistant",
        policy=policy,
        tools=[
            Tool("translate", lambda s: f"[fr] {s}", "translate to French"),
            Tool("summarize", lambda s: f"summary: {s[:20]}…", "summarize text"),
        ],
        trace=trace,
    )

    for task in [t("labs.lab01.desc_translate"), t("labs.lab01.desc_summarize")]:
        print(f"{t('ui.task')}: {task}\n  -> {agent.run(task)}")

    print(f"\n{t('ui.trace')} ({len(trace)} {t('ui.events')}):")
    for e in trace.events:
        print(" ", e["kind"], {k: v for k, v in e.items() if k not in ("t", "kind")})

    if not llm_enabled():
        print(f"\n{t('labs.lab01.try_llm')}")

    print(f"\n--- {t('exercises.heading')} ---")
    print(t("exercises.lab01_hint"))


if __name__ == "__main__":
    main()
