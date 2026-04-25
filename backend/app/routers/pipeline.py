from fastapi import APIRouter

from ..db import query_all

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

STAGE_ORDER = ["Ingesting", "Extracting", "Pricing", "HIL Review", "Approved"]

STAGE_META = {
    "Ingesting":  {"display": "Ingesting",              "border": "#1D4ED8", "color": "#1D4ED8", "icon": "📥"},
    "Extracting": {"display": "Extracting & Pricing",   "border": "#CF008B", "color": "#CF008B", "icon": "🔍"},
    "Pricing":    {"display": "Extracting & Pricing",   "border": "#CF008B", "color": "#CF008B", "icon": "🔍"},
    "HIL Review": {"display": "HIL Review",             "border": "#E4902E", "color": "#E4902E", "icon": "⏳"},
    "Approved":   {"display": "Approved & Delivered",   "border": "#16A34A", "color": "#16A34A", "icon": "✅"},
}


def _fmt_tcv(tcv_display: str | None, tcv_base: int | None) -> str:
    if tcv_display and tcv_display.strip():
        return tcv_display
    if not tcv_base:
        return "—"
    if tcv_base >= 10_000_000:
        return f"₹{tcv_base / 10_000_000:.1f}Cr"
    if tcv_base >= 100_000:
        return f"₹{tcv_base / 100_000:.1f}L"
    return f"₹{tcv_base:,}"


@router.get("/kanban")
def kanban():
    rows = query_all(
        """
        SELECT
            r.rfp_code,
            r.short_label,
            r.name,
            r.pricing_model,
            r.pipeline_stage,
            r.current_hil_level,
            r.status,
            r.tcv_display,
            r.tcv_base,
            r.risk_level,
            r.win_probability,
            r.category,
            c.name AS org
        FROM rfps r
        JOIN clients c ON c.id = r.client_id
        WHERE r.pipeline_stage IS NOT NULL
        ORDER BY r.active_pipeline_rank, r.created_at
        """
    )

    buckets: dict[str, list[dict]] = {s: [] for s in STAGE_ORDER}
    for r in rows:
        stage = r["pipeline_stage"]
        if stage not in buckets:
            continue

        label = r["short_label"] or r["name"] or r["rfp_code"]
        hil = r.get("current_hil_level")

        buckets[stage].append({
            "code":    r["rfp_code"],
            "name":    label,
            "org":     r["org"],
            "model":   r["pricing_model"] or "—",
            "tcv":     _fmt_tcv(r.get("tcv_display"), r.get("tcv_base")),
            "hil":     f"Level {hil}" if hil else "—",
            "status":  r["status"] or "Active",
            "category": r["category"] or "—",
            "risk":    r.get("risk_level") or "—",
            "winprob": r.get("win_probability"),
        })

    merged: dict[str, list[dict]] = {}
    for stage, deals in buckets.items():
        display = STAGE_META[stage]["display"]
        merged.setdefault(display, []).extend(deals)

    out = []
    seen = set()
    for stage in STAGE_ORDER:
        display = STAGE_META[stage]["display"]
        if display in seen:
            continue
        seen.add(display)
        out.append({
            "name":        display,
            "icon":        STAGE_META[stage]["icon"],
            "count":       len(merged.get(display, [])),
            "borderColor": STAGE_META[stage]["border"],
            "color":       STAGE_META[stage]["color"],
            "deals":       merged.get(display, []),
        })
    return out
