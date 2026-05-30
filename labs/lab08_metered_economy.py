"""Lab 08 - The economics of orchestration (Module 8, advanced track).

A full autonomous cycle through the real SDK: discover -> open payment channel
-> invoke (safety-gated) -> escrow debit -> signed receipt -> settle. You get a
bill-of-materials, just like a production agent paying for capabilities.

Run:  python labs/lab08_metered_economy.py   (COURSE_LANG=ru|es to localize)
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from courselib.economy import embedded_sandbox
from courselib.i18n import get_translator


def main() -> None:
    t = get_translator()
    print(f"== {t('modules.m8.title')} ==")

    with embedded_sandbox(budget=3.0) as econ:
        # The discovery *intent* stays in English so it matches the demo hub's
        # (English) capability catalog; only display text is localized. Searching
        # a real federated hub in any language is itself a later lab.
        res = econ.hire("translate text to multiple languages")
        bom = res.get("bill_of_materials")
        if not bom:
            print(res.get("note") or res.get("error") or "no capabilities matched")
            return

        print(f"{t('ui.task')}        :", res["task"])
        print(f"{t('ui.success')}     :", res["ok"])
        print(f"{t('ui.channel')}     :", bom["channel_id"] or t("ui.none"))
        print(f"{t('ui.total_spent')} :", f"${res['total_spent_usd']}")
        print(f"{t('ui.protocol')}    :", bom["protocol_version"])

        print(f"\n{t('ui.steps')}:")
        for step in bom["results"]:
            cid = step.get("capability_id") or step.get("result", {}).get("capability")
            print(f"  {t('ui.success')}={step.get('success')}  "
                  f"{t('ui.price')}=${step.get('price_usd')}  {cid}")

        cap = econ.capital_listings()
        listings = cap.get("listings", [])
        print(f"\n{t('ui.acex_listings')}: {len(listings)}")


if __name__ == "__main__":
    main()
