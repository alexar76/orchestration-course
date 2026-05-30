"""Lab 01 - The agent loop & tool use (Module 1).

Concept: an agent is a policy that decides which tool to call.
Industry map: MCP exposes tools to a model; here we make the decision
deterministic so you can see the loop with no LLM in the way.

Run:  python labs/lab01_agent_and_tool.py
      COURSE_LANG=ru python labs/lab01_agent_and_tool.py
      COURSE_LANG=es python labs/lab01_agent_and_tool.py
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.i18n import get_translator
from courselib.orchestration import Agent, Tool, Trace, keyword_policy


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m1.title')} ==")

    trace = Trace()
    agent = Agent(
        name="assistant",
        policy=keyword_policy({
            "translate": "translate", "summarize": "summarize",
            "переведи": "translate", "выжимк": "summarize",
            "traduce": "translate", "resume": "summarize",
        }),
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


if __name__ == "__main__":
    main()
