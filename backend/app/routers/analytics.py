from fastapi import APIRouter

from ..db import query_all, query_one

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


MODEL_GROUPS = {
    "Per Word/Min (45%)": {
        "color": "var(--primary)",
        "models": ("Per Word", "Per Hour", "Per 1,000 Words", "Per Min + Per Hr"),
    },
    "Annual Retainer (25%)": {
        "color": "var(--pink)",
        "models": ("Annual Retainer",),
    },
    "Fixed/Hybrid (18%)": {
        "color": "var(--cyan)",
        "models": ("Fixed Fee", "Hybrid", "Hybrid Fixed+T&M"),
    },
    "PMPM/Per Claim (12%)": {
        "color": "var(--success)",
        "models": ("PMPM", "Per Claim"),
    },
}

CATEGORY_GRADIENTS = {
    "IT Services":  "linear-gradient(180deg, #5929d0, #A855F7)",
    "BPO":          "linear-gradient(180deg, #CF008B, #F472B6)",
    "Translation":  "linear-gradient(180deg, #22D3EE, #67E8F9)",
    "Call Center":  "linear-gradient(180deg, #16A34A, #86EFAC)",
    "Interpretation": "linear-gradient(180deg, #F59E0B, #FCD34D)",
}


@router.get("/model-distribution")
def model_distribution():
    active = query_one(
        """
        SELECT COUNT(*) AS n FROM rfps
        WHERE status IN ('Active','Priced','Awarded')
        """
    )["n"]
    return {
        "total": active,
        "legend": [
            {"color": meta["color"], "label": label}
            for label, meta in MODEL_GROUPS.items()
        ],
    }


@router.get("/tcv-by-category")
def tcv_by_category():
    rows = query_all(
        """
        SELECT category, SUM(tcv_base) AS tcv_sum
        FROM rfps
        WHERE status IN ('Active','Priced','Awarded','Won')
        GROUP BY category
        ORDER BY tcv_sum DESC
        """
    )

    top3 = [r for r in rows[:3]]
    other_sum = sum(r["tcv_sum"] for r in rows[3:])

    max_tcv = max((r["tcv_sum"] for r in rows), default=1)
    scale = 4_000_000_000 / max_tcv if max_tcv else 0

    def _to_cr(rupees: int) -> str:
        return f"{rupees / 10_000_000:.2f}".rstrip("0").rstrip(".") or "0"

    out = []
    for r in top3:
        out.append({
            "label":     r["category"],
            "val":       _to_cr(r["tcv_sum"]),
            "heightPct": round(r["tcv_sum"] / max_tcv * 100, 1),
            "gradient":  CATEGORY_GRADIENTS.get(r["category"], "var(--gradient-banner)"),
        })
    if other_sum > 0:
        out.append({
            "label":     "Other",
            "val":       _to_cr(other_sum),
            "heightPct": round(other_sum / max_tcv * 100, 1),
            "gradient":  "linear-gradient(180deg, #16A34A, #86EFAC)",
        })
    return out


@router.get("/activity")
def activity():
    tiles = query_all(
        """
        SELECT variant, icon, value, label, trend_dir, trend_text
        FROM activity_snapshot
        ORDER BY sort_order
        """
    )
    top = query_one("SELECT summary FROM top_deal_today WHERE id = 1")
    return {
        "tiles": [
            {
                "variant": t["variant"],
                "icon":    t["icon"],
                "value":   t["value"],
                "label":   t["label"],
                "trend": {"dir": t["trend_dir"], "text": t["trend_text"]},
            }
            for t in tiles
        ],
        "topDeal": top["summary"] if top else "",
    }


@router.get("/accuracy")
def accuracy():
    buckets = query_all(
        """
        SELECT bucket_label, deal_count, in_sweet_spot, seq
        FROM accuracy_buckets
        ORDER BY seq
        """
    )
    total = sum(b["deal_count"] for b in buckets)
    sweet = sum(b["deal_count"] for b in buckets if b["in_sweet_spot"])

    return {
        "buckets": [
            {
                "label":   b["bucket_label"],
                "count":   b["deal_count"],
                "inSweet": bool(b["in_sweet_spot"]),
            }
            for b in buckets
        ],
        "insights": [
            {"lbl": "Within ±5%",     "val": f"{sweet} / {total}",
             "sub": f"{(sweet / total * 100) if total else 0:.0f}% accuracy",
             "color": "var(--success)"},
            {"lbl": "Mean Deviation", "val": "-0.2%",    "sub": "Near-zero bias",    "color": None},
            {"lbl": "Std. Deviation", "val": "σ = 2.8%", "sub": "Tight distribution", "color": None},
        ],
    }
