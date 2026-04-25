"""
Dataset inspector — prints distributions and volume-weighted stats.
Useful after scaling up to confirm the shape is what you expect.

Usage:
    python inspect.py --dir ./out
"""
import argparse
import csv
import json
from collections import Counter, defaultdict


def load(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dir", default="./out")
    args = p.parse_args()
    D = args.dir

    rfps       = load(f"{D}/rfp.csv")
    extracted  = load(f"{D}/extracted_data.csv")
    line_items = load(f"{D}/rfp_line_items.csv")
    deals      = load(f"{D}/deals.csv")
    pricing    = load(f"{D}/pricing_output.csv")

    print("\n=== SHAPE BY INDUSTRY ===")
    by_ind = Counter(r["industry"] for r in rfps)
    for ind, n in by_ind.most_common():
        print(f"  {ind:25s} {n:>6}")

    print("\n=== SERVICE MIX IN LINE ITEMS ===")
    svc_counts = Counter(li["service_type"] for li in line_items)
    for svc, n in svc_counts.most_common():
        print(f"  {svc:28s} {n:>6}")

    print("\n=== LOCALE MIX IN LINE ITEMS (top 15) ===")
    loc_counts = Counter(li["locale"] for li in line_items)
    for loc, n in loc_counts.most_common(15):
        print(f"  {loc:8s} {n:>6}")

    print("\n=== MARGIN DISTRIBUTION ===")
    margins = [float(d["margin_pct"]) for d in deals]
    if margins:
        margins.sort()
        def pct(p): return margins[int(len(margins)*p)]
        print(f"  min:  {min(margins):.1%}")
        print(f"  p25:  {pct(0.25):.1%}")
        print(f"  p50:  {pct(0.50):.1%}")
        print(f"  p75:  {pct(0.75):.1%}")
        print(f"  max:  {max(margins):.1%}")

    print("\n=== TCV (Total Contract Value) STATS ===")
    tcv_by_deal = defaultdict(float)
    for p_ in pricing:
        if p_["status"] == "COMPUTED":
            tcv_by_deal[p_["deal_id"]] += float(p_["line_total"])
    if tcv_by_deal:
        tcvs = sorted(tcv_by_deal.values())
        print(f"  deals with pricing:  {len(tcvs):,}")
        print(f"  total TCV across all deals:  ${sum(tcvs):,.0f}")
        print(f"  median deal TCV:             ${tcvs[len(tcvs)//2]:,.0f}")
        print(f"  p90 deal TCV:                ${tcvs[int(len(tcvs)*0.9)]:,.0f}")
        print(f"  max deal TCV:                ${max(tcvs):,.0f}")

    print("\n=== LINE ITEMS PER RFP ===")
    lis_per_rfp = Counter(li["rfp_id"] for li in line_items)
    if lis_per_rfp:
        vals = sorted(lis_per_rfp.values())
        print(f"  min: {min(vals)}  median: {vals[len(vals)//2]}  "
              f"max: {max(vals)}  avg: {sum(vals)/len(vals):.2f}")

    print("\n=== PRICING STATUS MIX ===")
    ps = Counter(p_["status"] for p_ in pricing)
    total_p = sum(ps.values())
    for s, n in ps.items():
        print(f"  {s:12s} {n:>7,}  ({100*n/total_p:.1f}%)")

    print("\n=== EXTRACTION CONFIDENCE BUCKETS ===")
    buckets = Counter()
    for e in extracted:
        c = float(e["confidence_score"])
        if c >= 0.90: buckets["high (≥0.90)"] += 1
        elif c >= 0.75: buckets["med (0.75-0.90)"] += 1
        elif c >= 0.60: buckets["low (0.60-0.75)"] += 1
        else: buckets["very low (<0.60)"] += 1
    for b, n in buckets.items():
        print(f"  {b:22s} {n:>6}")


if __name__ == "__main__":
    main()
