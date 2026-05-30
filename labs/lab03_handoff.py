"""Lab 03 - Handoffs & delegation (Module 3).

A front-desk agent delegates to a specialist via a Handoff. Control transfer
is the core of A2A and OpenAI Swarm; here it is explicit and bounded.

Run:  python labs/lab03_handoff.py   (COURSE_LANG=ru|es to localize)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.i18n import get_translator
from courselib.orchestration import Agent, Handoff, Tool, Trace, keyword_policy


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m3.title')} ==")
    trace = Trace()

    legal = Agent(
        "legal-specialist",
        policy=keyword_policy({"contract": "review", "nda": "review", "договор": "review"}),
        tools=[Tool("review", lambda s: "LEGAL OK: no red flags")],
        trace=trace,
    )

    def front_desk(task: str, agent: Agent):
        low = task.lower()
        if any(k in low for k in ("contract", "nda", "legal", "договор", "юридич")):
            return Handoff(to=legal, task=task, reason=t("labs.lab03.reason"))
        return f"[front-desk] {task}"

    front = Agent("front-desk", policy=front_desk, trace=trace)

    print(f"{t('ui.normal')} :", front.run(t("labs.lab03.book")))
    print(f"{t('ui.delegate')}:", front.run(t("labs.lab03.review")))

    print(f"\n{t('ui.handoffs')}:")
    for e in trace.of_kind("handoff"):
        print(f"  {e['frm']} -> {e['to']}  ({e['reason']})")


if __name__ == "__main__":
    main()
