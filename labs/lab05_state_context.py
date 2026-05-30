"""Lab 05 - State, memory & context (Module 5).

A StatefulPipeline threads a Context bag through stages — like a bill of
materials where each step adds artifacts instead of only passing strings.

Run:  python labs/lab05_state_context.py   (COURSE_LANG=ru|es to localize)
Exercise: python labs/run_exercises.py --module m5
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.i18n import get_translator
from courselib.orchestration import Context, StatefulPipeline, Trace


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m5.title')} ==")
    trace = Trace()

    def plan(ctx: Context) -> Context:
        spec = ctx.get("brief", t("labs.lab05.brief"))
        return ctx.set("plan", f"plan:{spec}").set("steps", ["copy", "design", "ship"])

    def build(ctx: Context) -> Context:
        artifacts = [f"{step}({ctx.get('plan')})" for step in ctx.get("steps", [])]
        return ctx.set("artifacts", artifacts).set("bom_count", len(artifacts))

    def summarize(ctx: Context) -> Context:
        return ctx.set("summary", t("labs.lab05.summary_fmt").format(n=ctx.get("bom_count", 0)))

    pipe = StatefulPipeline([plan, build, summarize], trace=trace)
    result = pipe.run({"brief": t("labs.lab05.brief")})

    print(f"{t('ui.task')}     : {result.get('brief')}")
    print(f"{t('labs.lab05.bom')} : {result.get('artifacts')}")
    print(f"{t('ui.result')}   : {result.get('summary')}")

    print(f"\n{t('ui.trace')} ({len(trace)} {t('ui.events')}):")
    for e in trace.of_kind("context_stage"):
        print(f"  stage {e['index']} keys={e['keys']}")

    print(f"\n--- {t('exercises.heading')} ---")
    print(t("exercises.lab05_hint"))


if __name__ == "__main__":
    main()
