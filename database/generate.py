"""
Centific Pricing Intelligence â€” Synthetic Dataset Generator
=========================================================

Single-file generator that produces all seven datasets at any scale.
Supports two modes:

    fresh    â€” builds everything from scratch at a given scale
    extend   â€” adds NEW rfps (+ extracted_data, line_items, deals, pricing)
               onto an existing dataset, preserving every existing row

Usage:
    python generate.py fresh  --rfps 1200 --out ./out
    python generate.py extend --rfps 500  --out ./out
    python generate.py fresh  --rfps 5000 --out ./out --seed 99

Scaling guide (approximate row counts):
    --rfps 500    â†’ ~5,500 total rows     (small pilot)
    --rfps 1000   â†’ ~10,000 total rows    (recommended default)
    --rfps 5000   â†’ ~47,000 total rows    (large training set)
    --rfps 10000  â†’ ~93,000 total rows    (full-scale production)

Every run produces the same seven CSVs:
    users.csv, cost_rates.csv, rfp.csv, extracted_data.csv,
    rfp_line_items.csv, deals.csv, pricing_output.csv

Phase 1 scope is enforced: no benchmarking, no multi-scenario pricing.
"""
import argparse
import csv
import json
import os
import random
import sys
import uuid
from collections import defaultdict, Counter
from datetime import datetime, timedelta

from config import (
    SERVICES, LOCALES, LOCALE_TIER, PRICING_MODELS, PRICING_MODEL_UNIT_AFFINITY,
    BASE_BUY_RATE, RFP_FORMATS, RFP_STATUSES, VOLUME_BANDS, INDUSTRIES,
    CLIENT_NAME_PARTS, FIRST_NAMES, LAST_NAMES, ROLE_MIX_RATIO,
    COVERAGE_BY_TIER, tier_bucket,
)

# -------------------------------------------------------------------
# Distribution constants (tuned from the Phase 1 MVP build)
# -------------------------------------------------------------------
# RFP status funnel â€” models the drop-off from upload to completion
STATUS_FUNNEL = [
    ("UPLOADED",   0.03),
    ("PROCESSING", 0.02),
    ("EXTRACTED",  0.10),
    ("PRICED",     0.12),
    ("APPROVED",   0.18),
    ("COMPLETED",  0.55),
]
FORMAT_MIX = [("PDF",0.60),("DOCX",0.30),("EXCEL",0.07),("SCANNED",0.03)]

# Statuses whose RFPs have advanced to pricing stage
PRICED_STATUSES = {"PRICED","APPROVED","COMPLETED"}
RFP_TO_DEAL_STATUS = {"PRICED":"DRAFT","APPROVED":"APPROVED","COMPLETED":"SUBMITTED"}
REJECTION_RATE = 0.06  # ~6% of approved-stage deals end up REJECTED

# Schemas (exact column order, matches TDD section 8)
SCHEMAS = {
    "users": ["user_id","name","email","role","created_at"],
    "cost_rates": ["rate_id","service_type","locale","buy_rate","currency",
                   "unit","effective_from","updated_by"],
    "rfp": ["rfp_id","file_name","format","status","uploaded_by","uploaded_at",
            "extraction_id","client_name","industry"],
    "extracted_data": ["extraction_id","rfp_id","pricing_model","volume_low",
                       "volume_base","volume_high","service_types","locales",
                       "sla_terms","commercial_terms","confidence_score"],
    "rfp_line_items": ["line_item_id","rfp_id","service_type","locale","unit",
                       "volume_low","volume_base","volume_high","cost_rate_id"],
    "deals": ["deal_id","rfp_id","overhead_pct","margin_pct","status",
              "created_by","created_at","approved_by","approved_at"],
    "pricing_output": ["pricing_id","deal_id","line_item_id","service_type",
                       "locale","unit","volume","buy_rate","overhead_pct",
                       "margin_pct","sell_rate","line_total","currency","status"],
}


# ===================================================================
# IO HELPERS
# ===================================================================
def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return list(csv.DictReader(f))

def write_csv(rows, path, fields):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def append_csv(rows, path, fields):
    """Append without rewriting the header if file exists."""
    exists = os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if not exists:
            w.writeheader()
        w.writerows(rows)

def weighted_choice(pairs):
    values, weights = zip(*pairs)
    return random.choices(values, weights=weights, k=1)[0]


# ===================================================================
# FOUNDATION GENERATORS (users, cost_rates)
# ===================================================================
def gen_users(n_users):
    """Derive per-role counts from the ratio, guaranteeing at least 1 of each role."""
    users = []
    allocations = []
    for role, ratio in ROLE_MIX_RATIO:
        allocations.append((role, max(1, int(round(ratio * n_users)))))
    # Fix rounding drift so total == n_users
    total = sum(n for _, n in allocations)
    drift = n_users - total
    if drift:  # adjust ANALYST (largest bucket) to absorb rounding
        allocations[0] = (allocations[0][0], allocations[0][1] + drift)

    base_date = datetime(2025, 1, 1)
    uid_counter = 1
    for role, count in allocations:
        for _ in range(count):
            first = random.choice(FIRST_NAMES)
            last  = random.choice(LAST_NAMES)
            uid = str(uuid.UUID(int=uid_counter)); uid_counter += 1
            users.append({
                "user_id":    uid,
                "name":       f"{first} {last}",
                "email":      f"{first.lower()}.{last.lower()}{uid_counter}@company.com",
                "role":       role,
                "created_at": (base_date + timedelta(days=random.randint(0,400))).isoformat(),
            })
    random.shuffle(users)
    return users


def gen_cost_rates(users):
    """Build master buy-rate catalog (service Ã— locale) with realistic coverage gaps."""
    updaters = [u["user_id"] for u in users if u["role"] in ("ADMIN","OPS")]
    if not updaters:
        updaters = [users[0]["user_id"]]  # fallback

    rates = []
    base_date = datetime(2024, 10, 1)
    for service, meta in SERVICES.items():
        unit     = meta["unit"]
        category = meta["category"]
        base     = BASE_BUY_RATE[service][unit]
        for locale in LOCALES:
            tier = tier_bucket(locale)
            if random.random() > COVERAGE_BY_TIER[tier][category]:
                continue  # intentional coverage gap
            multiplier = LOCALE_TIER[locale] * random.uniform(0.92, 1.08)
            rates.append({
                "rate_id":        str(uuid.uuid4()),
                "service_type":   service,
                "locale":         locale,
                "buy_rate":       round(base * multiplier, 4),
                "currency":       "USD",
                "unit":           unit,
                "effective_from": (base_date + timedelta(days=random.randint(0,500))).date().isoformat(),
                "updated_by":     random.choice(updaters),
            })
    return rates


# ===================================================================
# RFP SHAPE & LINE ITEM HELPERS
# ===================================================================
def pick_rfp_shape():
    """Returns (n_services, n_locales). Biased toward small/mid RFPs."""
    shape = weighted_choice([("small",0.55),("mid",0.35),("large",0.10)])
    if shape == "small": return 1, random.randint(1,2)
    if shape == "mid":   return random.randint(1,2), random.randint(2,4)
    return random.randint(2,4), random.randint(4,8)

def volume_triplet(unit):
    lo_floor, hi_ceil = VOLUME_BANDS[unit]
    base = random.randint(int(lo_floor*1.5), int(hi_ceil*0.4))
    return (int(base*random.uniform(0.5,0.75)),
            base,
            int(base*random.uniform(1.3,1.8)))

def pick_pricing_model(units):
    candidates = set()
    for u in units:
        candidates.update(PRICING_MODEL_UNIT_AFFINITY.get(u, ["FIXED"]))
    return random.choice(list(candidates)) if candidates else "FIXED"

def gen_client_name():
    return (f"{random.choice(CLIENT_NAME_PARTS['prefix'])} "
            f"{random.choice(CLIENT_NAME_PARTS['core'])} "
            f"{random.choice(CLIENT_NAME_PARTS['suffix'])}")


# ===================================================================
# RFP / EXTRACTED / LINE ITEMS GENERATION
# ===================================================================
def gen_rfps(n_rfps, users, cost_rates, upload_start_date):
    """
    Generates rfp, extracted_data, rfp_line_items in one pass
    to guarantee referential consistency.
    """
    analysts = [u for u in users if u["role"] == "ANALYST"]
    if not analysts:
        raise RuntimeError("No ANALYST users available â€” increase --users or seed foundation first.")

    rate_idx = {(r["service_type"], r["locale"]): r for r in cost_rates}
    svc_locales = defaultdict(list)
    for r in cost_rates:
        svc_locales[r["service_type"]].append(r["locale"])

    rfps, extracted, line_items = [], [], []

    for _ in range(n_rfps):
        rfp_id        = str(uuid.uuid4())
        extraction_id = str(uuid.uuid4())
        uploader      = random.choice(analysts)
        uploaded_at   = upload_start_date + timedelta(
            days=random.randint(0, 320),
            hours=random.randint(0,23),
            minutes=random.randint(0,59),
        )
        status    = weighted_choice(STATUS_FUNNEL)
        fmt       = weighted_choice(FORMAT_MIX)
        industry  = random.choice(INDUSTRIES)
        client    = gen_client_name()

        n_services, n_locales = pick_rfp_shape()
        services_picked = random.sample(list(SERVICES.keys()),
                                        k=min(n_services, len(SERVICES)))
        union_locales = list({l for s in services_picked for l in svc_locales.get(s, [])})
        if not union_locales:
            continue
        locales_picked = random.sample(union_locales,
                                       k=min(n_locales, len(union_locales)))

        # Build line items
        rfp_lis = []
        units_in_rfp = set()
        for svc in services_picked:
            svc_unit = SERVICES[svc]["unit"]
            units_in_rfp.add(svc_unit)
            for loc in locales_picked:
                if (svc, loc) not in rate_idx:
                    # Drop most missing combos; keep ~30% as genuine unmapped gaps
                    if random.random() < 0.7:
                        continue
                low, base_v, high = volume_triplet(svc_unit)
                rate_row = rate_idx.get((svc, loc))
                li = {
                    "line_item_id": str(uuid.uuid4()),
                    "rfp_id":       rfp_id,
                    "service_type": svc,
                    "locale":       loc,
                    "unit":         svc_unit,
                    "volume_low":   low,
                    "volume_base":  base_v,
                    "volume_high":  high,
                    "cost_rate_id": rate_row["rate_id"] if rate_row else "",
                }
                rfp_lis.append(li)

        if not rfp_lis:
            continue
        line_items.extend(rfp_lis)

        # Aggregate volumes for extracted_data
        agg_low  = sum(li["volume_low"]  for li in rfp_lis)
        agg_base = sum(li["volume_base"] for li in rfp_lis)
        agg_high = sum(li["volume_high"] for li in rfp_lis)

        # Confidence scoring
        conf = 0.92
        if fmt == "SCANNED":       conf -= 0.18
        if len(locales_picked) > 8: conf -= 0.08
        conf = round(max(0.45, min(0.99, conf + random.uniform(-0.08,0.05))), 2)

        sla_terms = {
            "response_time_hours": random.choice([4,8,24,48]),
            "uptime_target_pct":   random.choice([99.0,99.5,99.9]),
            "penalty_clause":      random.choice([True,False]),
            "penalty_rate_pct":    round(random.uniform(2,10),1),
        }
        commercial_terms = {
            "duration_months":      random.choice([12,24,36]),
            "renewal":              random.choice(["auto","manual","none"]),
            "tax_treatment":        random.choice(["exclusive","inclusive"]),
            "volume_tolerance_pct": random.choice([5,10,15,20]),
            "payment_terms_days":   random.choice([30,45,60]),
        }
        sla_json = json.dumps(sla_terms)
        if conf < 0.70 and random.random() < 0.3:
            sla_json = ""  # missing â€” HIL Level 1 must validate

        extracted.append({
            "extraction_id":    extraction_id,
            "rfp_id":           rfp_id,
            "pricing_model":    pick_pricing_model(units_in_rfp),
            "volume_low":       agg_low,
            "volume_base":      agg_base,
            "volume_high":      agg_high,
            "service_types":    json.dumps(services_picked),
            "locales":          json.dumps(locales_picked),
            "sla_terms":        sla_json,
            "commercial_terms": json.dumps(commercial_terms),
            "confidence_score": conf,
        })

        ext = "pdf" if fmt == "SCANNED" else fmt.lower()
        rfps.append({
            "rfp_id":        rfp_id,
            "file_name":     f"RFP_{client.replace(' ','_')}_{uploaded_at.strftime('%Y%m')}.{ext}",
            "format":        fmt,
            "status":        status,
            "uploaded_by":   uploader["user_id"],
            "uploaded_at":   uploaded_at.isoformat(),
            "extraction_id": extraction_id,
            "client_name":   client,
            "industry":      industry,
        })

    return rfps, extracted, line_items


# ===================================================================
# DEAL & PRICING GENERATION
# ===================================================================
def gen_deals_and_pricing(rfps, line_items, cost_rates, users):
    analysts = [u["user_id"] for u in users if u["role"] == "ANALYST"]
    managers = [u["user_id"] for u in users if u["role"] == "MANAGER"]
    if not managers:  # safety net
        managers = analysts

    rate_by_id = {r["rate_id"]: r for r in cost_rates}
    li_by_rfp  = defaultdict(list)
    for li in line_items:
        li_by_rfp[li["rfp_id"]].append(li)

    deals, pricing = [], []
    for rfp in rfps:
        if rfp["status"] not in PRICED_STATUSES:
            continue
        rfp_lis = li_by_rfp.get(rfp["rfp_id"], [])
        if not rfp_lis:
            continue

        # Industry-linked margin/overhead bands
        ind = rfp["industry"]
        if ind in ("Government","Education"):
            margin_pct   = round(random.uniform(0.12,0.20),3)
            overhead_pct = round(random.uniform(0.08,0.12),3)
        elif ind in ("Healthcare","Legal","Life Sciences"):
            margin_pct   = round(random.uniform(0.25,0.40),3)
            overhead_pct = round(random.uniform(0.10,0.15),3)
        else:
            margin_pct   = round(random.uniform(0.18,0.30),3)
            overhead_pct = round(random.uniform(0.08,0.14),3)

        base_status = RFP_TO_DEAL_STATUS[rfp["status"]]
        if base_status == "APPROVED" and random.random() < REJECTION_RATE:
            base_status = "REJECTED"

        uploaded_at = datetime.fromisoformat(rfp["uploaded_at"])
        created_at  = uploaded_at + timedelta(days=random.randint(1,5))
        approved_at, approved_by = None, ""
        if base_status in ("APPROVED","SUBMITTED"):
            approved_at = created_at + timedelta(days=random.randint(1,4))
            approved_by = random.choice(managers)

        deal_id = str(uuid.uuid4())
        creator = rfp["uploaded_by"] if rfp["uploaded_by"] in analysts else random.choice(analysts)

        deals.append({
            "deal_id":      deal_id,
            "rfp_id":       rfp["rfp_id"],
            "overhead_pct": overhead_pct,
            "margin_pct":   margin_pct,
            "status":       base_status,
            "created_by":   creator,
            "created_at":   created_at.isoformat(),
            "approved_by":  approved_by,
            "approved_at":  approved_at.isoformat() if approved_at else "",
        })

        # BR-PI-005: sell_rate = buy_rate * (1 + overhead_pct + margin_pct)
        for li in rfp_lis:
            rate_row = rate_by_id.get(li["cost_rate_id"])
            if not rate_row:
                # Unmapped â€” status flag routes to HIL (BR-PI-012)
                pricing.append({
                    "pricing_id":   str(uuid.uuid4()),
                    "deal_id":      deal_id,
                    "line_item_id": li["line_item_id"],
                    "service_type": li["service_type"],
                    "locale":       li["locale"],
                    "unit":         li["unit"],
                    "volume":       li["volume_base"],
                    "buy_rate":     "",
                    "overhead_pct": overhead_pct,
                    "margin_pct":   margin_pct,
                    "sell_rate":    "",
                    "line_total":   "",
                    "currency":     "USD",
                    "status":       "UNMAPPED",
                })
                continue

            buy_rate   = float(rate_row["buy_rate"])
            volume     = int(li["volume_base"])
            sell_rate  = round(buy_rate * (1 + overhead_pct + margin_pct), 4)
            line_total = round(sell_rate * volume, 2)
            pricing.append({
                "pricing_id":   str(uuid.uuid4()),
                "deal_id":      deal_id,
                "line_item_id": li["line_item_id"],
                "service_type": li["service_type"],
                "locale":       li["locale"],
                "unit":         li["unit"],
                "volume":       volume,
                "buy_rate":     buy_rate,
                "overhead_pct": overhead_pct,
                "margin_pct":   margin_pct,
                "sell_rate":    sell_rate,
                "line_total":   line_total,
                "currency":     "USD",
                "status":       "COMPUTED",
            })

    return deals, pricing


# ===================================================================
# ORCHESTRATORS
# ===================================================================
def run_fresh(out_dir, n_rfps, n_users, seed):
    random.seed(seed)
    os.makedirs(out_dir, exist_ok=True)
    print(f"[fresh] scale: n_rfps={n_rfps}, n_users={n_users}, seed={seed}")

    users      = gen_users(n_users)
    cost_rates = gen_cost_rates(users)
    rfps, extracted, line_items = gen_rfps(
        n_rfps, users, cost_rates, datetime(2025, 6, 1)
    )
    deals, pricing = gen_deals_and_pricing(rfps, line_items, cost_rates, users)

    write_csv(users,      f"{out_dir}/users.csv",          SCHEMAS["users"])
    write_csv(cost_rates, f"{out_dir}/cost_rates.csv",     SCHEMAS["cost_rates"])
    write_csv(rfps,       f"{out_dir}/rfp.csv",            SCHEMAS["rfp"])
    write_csv(extracted,  f"{out_dir}/extracted_data.csv", SCHEMAS["extracted_data"])
    write_csv(line_items, f"{out_dir}/rfp_line_items.csv", SCHEMAS["rfp_line_items"])
    write_csv(deals,      f"{out_dir}/deals.csv",          SCHEMAS["deals"])
    write_csv(pricing,    f"{out_dir}/pricing_output.csv", SCHEMAS["pricing_output"])

    _print_summary(out_dir, users, cost_rates, rfps, extracted, line_items, deals, pricing)


def run_extend(out_dir, n_new_rfps, seed):
    """
    Append new RFPs to an existing dataset without touching any existing rows.
    users & cost_rates are reused as-is; only transactional tables grow.
    """
    random.seed(seed)
    required = ["users.csv","cost_rates.csv","rfp.csv","extracted_data.csv",
                "rfp_line_items.csv","deals.csv","pricing_output.csv"]
    for f in required:
        if not os.path.exists(f"{out_dir}/{f}"):
            print(f"[extend] ERROR: {f} not found in {out_dir}. Run fresh mode first.", file=sys.stderr)
            sys.exit(1)

    print(f"[extend] adding {n_new_rfps} new RFPs to {out_dir}, seed={seed}")
    users      = read_csv(f"{out_dir}/users.csv")
    cost_rates = read_csv(f"{out_dir}/cost_rates.csv")

    # Start new uploads AFTER the existing latest upload to keep the timeline clean
    existing_rfps = read_csv(f"{out_dir}/rfp.csv")
    if existing_rfps:
        latest = max(datetime.fromisoformat(r["uploaded_at"]) for r in existing_rfps)
        start_date = latest + timedelta(days=1)
    else:
        start_date = datetime(2025, 6, 1)

    new_rfps, new_extracted, new_lis = gen_rfps(
        n_new_rfps, users, cost_rates, start_date
    )
    new_deals, new_pricing = gen_deals_and_pricing(new_rfps, new_lis, cost_rates, users)

    append_csv(new_rfps,      f"{out_dir}/rfp.csv",            SCHEMAS["rfp"])
    append_csv(new_extracted, f"{out_dir}/extracted_data.csv", SCHEMAS["extracted_data"])
    append_csv(new_lis,       f"{out_dir}/rfp_line_items.csv", SCHEMAS["rfp_line_items"])
    append_csv(new_deals,     f"{out_dir}/deals.csv",          SCHEMAS["deals"])
    append_csv(new_pricing,   f"{out_dir}/pricing_output.csv", SCHEMAS["pricing_output"])

    print(f"[extend] added: rfp+{len(new_rfps)}  extracted+{len(new_extracted)}  "
          f"line_items+{len(new_lis)}  deals+{len(new_deals)}  pricing+{len(new_pricing)}")


def _print_summary(out_dir, users, cost_rates, rfps, extracted, line_items, deals, pricing):
    print("\n--- row counts ---")
    for name, rows in [("users",users),("cost_rates",cost_rates),("rfp",rfps),
                       ("extracted_data",extracted),("rfp_line_items",line_items),
                       ("deals",deals),("pricing_output",pricing)]:
        print(f"  {name:18s} {len(rows):>8,}")
    total = sum(len(x) for x in [users,cost_rates,rfps,extracted,line_items,deals,pricing])
    print(f"  {'TOTAL':18s} {total:>8,}")
    print("\nWritten to:", out_dir)


# ===================================================================
# CLI
# ===================================================================
def main():
    p = argparse.ArgumentParser(description="Centific Pricing Intelligence dataset generator")
    p.add_argument("mode", choices=["fresh","extend"], help="generation mode")
    p.add_argument("--rfps", type=int, required=True, help="number of RFPs to generate")
    p.add_argument("--users", type=int, default=50, help="number of users (fresh mode only)")
    p.add_argument("--out", type=str, default="./out", help="output directory")
    p.add_argument("--seed", type=int, default=42, help="random seed")
    args = p.parse_args()

    if args.mode == "fresh":
        run_fresh(args.out, args.rfps, args.users, args.seed)
    else:
        run_extend(args.out, args.rfps, args.seed)


if __name__ == "__main__":
    main()
