"""Lab 04 - Discovery & invocation (Module 4).

Uses hub-lite (~5 MB deps, no git clones). Same discover → invoke → receipt
pattern as production AIMarket. For the full SDK cycle see lab08.

Run:  python labs/lab04_discover_invoke.py   (COURSE_LANG=ru|es to localize)
Needs: pip install -e ".[hub-lite]"
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.hub_lite import embedded_hub_lite
from courselib.i18n import get_translator


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m4.title')} ==")

    with embedded_hub_lite() as hub:
        print(f"{t('ui.hub')}:", hub.well_known().get("name"))

        print(f"\n{t('ui.discover')}('translate'):")
        for m in hub.discover("translate")[:5]:
            print(f"  {m.get('product_id')}/{m.get('capability_id')}"
                  f"  ${m.get('price_per_call_usd')}")

        print(f"\n{t('labs.lab04.invoking')}:")
        out = hub.invoke("prod-translate", "translate.multi@v2", {"text": "hello world"})
        print(f"  {t('ui.success')}     :", out.get("success"))
        print(f"  {t('ui.price')}       :", out.get("price_usd"))
        print(f"  {t('ui.served_by')}   :", out.get("result", {}).get("output", {}).get("served_by"))
        print(f"  {t('ui.receipt')}     :", (out.get("receipt") or {}).get("nonce", "n/a"))


if __name__ == "__main__":
    main()
