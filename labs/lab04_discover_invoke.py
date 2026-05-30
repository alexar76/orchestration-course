"""Lab 04 - Discovery & invocation against the REAL economy (Module 4).

Same orchestration patterns from labs 1-3, now executed against a live AIMarket
hub via the genuine aimarket-agent SDK. The hub + a stub factory are booted
locally (no infra, no money). Swap COURSE_HUB_URL to go against a real hub.

Run:  python labs/lab04_discover_invoke.py   (COURSE_LANG=ru|es to localize)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.economy import embedded_sandbox
from courselib.i18n import get_translator


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m4.title')} ==")

    with embedded_sandbox() as econ:
        print(f"{t('ui.hub')}:", econ.well_known().get("name"))

        print(f"\n{t('ui.discover')}('translate'):")
        for m in econ.discover("translate")[:5]:
            print(f"  {m.get('product_id')}/{m.get('capability_id')}"
                  f"  ${m.get('price_per_call_usd')}")

        print(f"\n{t('labs.lab04.invoking')}:")
        out = econ.invoke("prod-translate", "translate.multi@v2", {"text": "hello world"})
        print(f"  {t('ui.success')}     :", out.get("success"))
        print(f"  {t('ui.price')}       :", out.get("price_usd"))
        print(f"  {t('ui.served_by')}   :", out.get("result", {}).get("output", {}).get("served_by"))
        print(f"  {t('ui.receipt')}     :", (out.get("receipt") or {}).get("nonce", "n/a"))


if __name__ == "__main__":
    main()
