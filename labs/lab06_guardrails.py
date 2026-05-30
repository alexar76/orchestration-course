"""Lab 06 - Guardrails & safety (Module 6).

Pre/post guardrails wrap tools to block prompt injection and oversized output
before unsafe content reaches downstream agents or users.

Run:  python labs/lab06_guardrails.py   (COURSE_LANG=ru|es to localize)
Exercise: python labs/run_exercises.py --module m6
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.i18n import get_translator
from courselib.orchestration import Tool, Trace, guarded_tool, injection_guardrail, length_guardrail


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m6.title')} ==")
    trace = Trace()

    echo = Tool("echo", lambda s: s.upper(), "echo input")
    safe_echo = guarded_tool(echo, [injection_guardrail(), length_guardrail(120)], trace)

    safe_task = t("labs.lab06.safe_task")
    attack = t("labs.lab06.attack_task")

    print(f"{t('ui.normal')} : {safe_echo(safe_task)}")
    print(f"{t('labs.lab06.blocked')} : {safe_echo(attack)}")

    print(f"\n{t('ui.trace')}:")
    for e in trace.events:
        if e["kind"] in ("guardrail_block", "tool_call"):
            print(" ", e["kind"], {k: v for k, v in e.items() if k not in ("t", "kind")})

    print(f"\n--- {t('exercises.heading')} ---")
    print(t("exercises.lab06_hint"))


if __name__ == "__main__":
    main()
