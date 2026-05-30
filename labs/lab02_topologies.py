"""Lab 02 - Orchestration topologies (Module 2).

Sequential (pipeline), Parallel (fan-out), Router (pick-one).
Industry map: LangGraph graphs / CrewAI crews build these same shapes.

Run:  python labs/lab02_topologies.py   (COURSE_LANG=ru|es to localize)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.i18n import get_translator
from courselib.orchestration import Agent, Parallel, Router, Sequential, Tool, keyword_policy


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m2.title')} ==")

    pipeline = Sequential([
        lambda spec: f"draft({spec})",
        lambda draft: f"reviewed({draft})",
        lambda doc: f"published({doc})",
    ])
    print(f"{t('ui.sequential')}:", pipeline.run("landing-page"))

    fanout = Parallel([
        lambda b: f"copy:{b}",
        lambda b: f"design:{b}",
        lambda b: f"seo:{b}",
    ])
    print(f"{t('ui.parallel')}:", fanout.run("agents"))

    es = Agent("es", policy=keyword_policy({"hola": "greet"}),
               tools=[Tool("greet", lambda s: "respuesta en espanol")])
    en = Agent("en", policy=keyword_policy({"hello": "greet"}),
               tools=[Tool("greet", lambda s: "answer in english")])
    router = Router(routes=[
        (lambda x: "hola" in x.lower(), es),
        (lambda x: "hello" in x.lower(), en),
    ])
    print(f"{t('ui.router_es')}:", router.run("hola equipo"))
    print(f"{t('ui.router_en')}:", router.run("hello team"))


if __name__ == "__main__":
    main()
