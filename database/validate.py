"""
Validator for the Centific Pricing Intelligence dataset.
Works at any scale. Usage:

    python validate.py --dir ./out
"""
import argparse
import csv
import json
import os
from collections import Counter


def load(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def banner(s):
    print("\n" + "="*70)
    print(s)
    print("="*70)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="./out", help="dataset directory")
    args = p.parse_args()
    D = args.dir

    users      = load(f"{D}/users.csv")
    cost_rates = load(f"{D}/cost_rates.csv")
    rfps       = load(f"{D}/rfp.csv")
    extracted  = load(f"{D}/extracted_data.csv")
    line_items = load(f"{D}/rfp_line_items.csv")
    deals      = load(f"{D}/deals.csv")
    pricing    = load(f"{D}/pricing_output.csv")

    banner("ROW COUNTS")
    counts = {
        "users": len(users),               "cost_rates": len(cost_rates),
        "rfp": len(rfps),                  "extracted_data": len(extracted),
        "rfp_line_items": len(line_items), "deals": len(deals),
        "pricing_output": len(pricing),
    }
    for k, v in counts.items():
        print(f"  {k:20s} {v:>10,}")
    print(f"  {'TOTAL':20s} {sum(counts.values()):>10,}")

    banner("REFERENTIAL INTEGRITY")
    user_ids   = {u["user_id"] for u in users}
    rate_ids   = {r["rate_id"] for r in cost_rates}
    rfp_ids    = {r["rfp_id"]  for r in rfps}
    ext_ids    = {e["extraction_id"] for e in extracted}
    deal_ids   = {d["deal_id"] for d in deals}
    li_ids     = {li["line_item_id"] for li in line_items}

    errors = []
    for r in rfps:
        if r["uploaded_by"] not in user_ids: errors.append("rfpâ†’uploader")
        if r["extraction_id"] not in ext_ids: errors.append("rfpâ†’extraction")
    for e in extracted:
        if e["rfp_id"] not in rfp_ids: errors.append("extractedâ†’rfp")
    for li in line_items:
        if li["rfp_id"] not in rfp_ids: errors.append("line_itemâ†’rfp")
        if li["cost_rate_id"] and li["cost_rate_id"] not in rate_ids:
            errors.append("line_itemâ†’rate")
    for d in deals:
        if d["rfp_id"] not in rfp_ids: errors.append("dealâ†’rfp")
        if d["created_by"] not in user_ids: errors.append("dealâ†’creator")
        if d["approved_by"] and d["approved_by"] not in user_ids:
            errors.append("dealâ†’approver")
    for px in pricing:
        if px["deal_id"] not in deal_ids: errors.append("pricingâ†’deal")
        if px["line_item_id"] not in li_ids: errors.append("pricingâ†’line_item")

    if errors:
        ec = Counter(errors)
        print(f"  âœ— {sum(ec.values())} referential errors")
        for k, v in ec.items():
            print(f"    - {k}: {v}")
    else:
        print("  âœ“ all foreign keys resolve cleanly")

    banner("BUSINESS RULE CHECKS")
    # BR-PI-005
    formula_err = 0
    for p_ in pricing:
        if p_["status"] != "COMPUTED": continue
        br = float(p_["buy_rate"]); oh = float(p_["overhead_pct"])
        mg = float(p_["margin_pct"]); sr = float(p_["sell_rate"])
        if abs(round(br*(1+oh+mg),4) - sr) > 1e-3: formula_err += 1
    print(f"  BR-PI-005 pricing formula:           {'âœ“' if formula_err==0 else f'âœ— {formula_err}'}")

    cs_err = sum(1 for p_ in pricing if p_["status"]=="COMPUTED"
                 and float(p_["sell_rate"]) <= float(p_["buy_rate"]))
    print(f"  Cost < Sell on all priced rows:      {'âœ“' if cs_err==0 else f'âœ— {cs_err}'}")

    vol_err = sum(1 for li in line_items
                  if not (int(li["volume_low"]) <= int(li["volume_base"]) <= int(li["volume_high"])))
    print(f"  Volume ordering low â‰¤ base â‰¤ high:   {'âœ“' if vol_err==0 else f'âœ— {vol_err}'}")

    hil_err = sum(1 for d in deals
                  if d["status"] in ("APPROVED","SUBMITTED") and not d["approved_by"])
    print(f"  BR-PI-008 HIL approval captured:     {'âœ“' if hil_err==0 else f'âœ— {hil_err}'}")

    json_err = 0
    for e in extracted:
        for fld in ("service_types","locales","commercial_terms"):
            try: json.loads(e[fld])
            except: json_err += 1
        if e["sla_terms"]:
            try: json.loads(e["sla_terms"])
            except: json_err += 1
    print(f"  JSON fields well-formed:             {'âœ“' if json_err==0 else f'âœ— {json_err}'}")

    banner("REALISM")
    rates_kv = {(r["service_type"], r["locale"]): float(r["buy_rate"]) for r in cost_rates}
    checks = [
        ("translation en-IN < en-US",
         rates_kv.get(("translation","en-IN"),0) < rates_kv.get(("translation","en-US"),999)),
        ("transcreation > translation (en-US)",
         rates_kv.get(("transcreation","en-US"),0) > rates_kv.get(("translation","en-US"),0)),
        ("dubbing > subtitling > transcription (en-US)",
         rates_kv.get(("dubbing","en-US"),0) >
         rates_kv.get(("subtitling","en-US"),0) >
         rates_kv.get(("transcription","en-US"),0)),
    ]
    for label, ok in checks:
        print(f"  {'âœ“' if ok else 'âœ—'}  {label}")
    mg_bad = sum(1 for d in deals if not (0.10 <= float(d["margin_pct"]) <= 0.45))
    print(f"  Margins in 10â€“45% band:              {'âœ“' if mg_bad==0 else f'âœ— {mg_bad}'}")
    if extracted:
        low_conf = sum(1 for e in extracted if float(e["confidence_score"]) < 0.70)
        print(f"  Low-confidence extractions:          "
              f"{low_conf}/{len(extracted)} ({100*low_conf/len(extracted):.1f}%)")

    banner("DISTRIBUTIONS")
    print("  RFP status: ", dict(Counter(r["status"] for r in rfps)))
    print("  RFP format: ", dict(Counter(r["format"] for r in rfps)))
    print("  Deal status:", dict(Counter(d["status"] for d in deals)))
    print("  Pricing:    ", dict(Counter(p_["status"] for p_ in pricing)))

    banner("DONE")


if __name__ == "__main__":
    main()
