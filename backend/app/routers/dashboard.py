from fastapi import APIRouter, HTTPException, Query

from ..db import query_all, query_one, rows_to_dicts

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _current_rfp_code() -> str:
    row = query_one("SELECT rfp_code FROM rfps WHERE is_current = TRUE LIMIT 1")
    if row is None:
        raise HTTPException(status_code=500, detail="No current RFP configured")
    return row["rfp_code"]


def _format_inr_compact(rupees: int) -> str:
    if rupees >= 10_000_000:
        return f"₹{rupees / 10_000_000:.1f}Cr"
    if rupees >= 100_000:
        return f"₹{rupees / 100_000:.1f}L"
    return f"₹{rupees:,}"


@router.get("/kpis")
def kpis():
    active_statuses = ("Active", "Priced", "Awarded")

    placeholders = ",".join(["%s"] * len(active_statuses))

    rfp_count = query_one(
        f"SELECT COUNT(*) AS n FROM rfps WHERE status IN ({placeholders})",
        active_statuses,
    )["n"]

    tcv_total = query_one(
        f"SELECT COALESCE(SUM(tcv_base), 0) AS s FROM rfps WHERE status IN ({placeholders})",
        active_statuses,
    )["s"]

    win_row = query_one(
        "SELECT win_rate_pct FROM win_rate_points WHERE range_type = 'quarter' ORDER BY seq DESC LIMIT 1"
    )
    win_pct = win_row["win_rate_pct"] if win_row else 0

    pending = query_one("SELECT COUNT(*) AS n FROM approvals WHERE status = 'pending'")["n"]

    return {
        "rfps_in_pipeline": {
            "value":  str(rfp_count),
            "label":  "RFPs in Pipeline",
            "sub":    f"{pending} awaiting HIL approval",
            "trend":  "↑ 12%",
            "trend_dir": "up",
            "icon_variant": "purple",
            "icon": "📄",
        },
        "tcv_total": {
            "value":  _format_inr_compact(tcv_total),
            "label":  "Total Contract Value (TCV)",
            "sub":    "Across all active deals",
            "trend":  "↑ 8%",
            "trend_dir": "up",
            "icon_variant": "pink",
            "icon": "💎",
        },
        "win_rate": {
            "value":  f"{win_pct}%",
            "label":  "Win Rate (Last 90 days)",
            "sub":    "vs 65% prior quarter",
            "trend":  "↑ 3%",
            "trend_dir": "up",
            "icon_variant": "cyan",
            "icon": "🎯",
        },
        "pending_approvals": pending,
    }


@router.get("/pipeline")
def active_pipeline():
    rows = query_all(
        """
        SELECT
            r.rfp_code,
            r.short_label,
            c.name           AS org,
            r.pricing_model,
            r.tcv_display,
            r.pipeline_stage,
            r.current_hil_level,
            r.status
        FROM rfps r
        JOIN clients c ON c.id = r.client_id
        WHERE r.active_in_pipeline = TRUE
        ORDER BY r.active_pipeline_rank
        """
    )

    stage_variant = {
        "Ingesting":  "ingest",
        "Extracting": "extract",
        "Pricing":    "pricing",
        "HIL Review": "hil",
        "Approved":   "approved",
    }

    def _hil_tag(level: int | None, status: str) -> dict:
        if status == "Awarded":
            return {"label": "Complete", "variant": "green"}
        if status == "Active" and (level is None or level == 0):
            return {"label": "—", "variant": "purple"}
        variant_by_lvl = {1: "blue", 2: "orange", 3: "orange", 4: "pink", 5: "pink"}
        return {"label": f"Level {level}", "variant": variant_by_lvl.get(level, "purple")}

    def _actions_for(stage: str, status: str) -> list[dict]:
        if status == "Awarded":
            return [{"label": "Template"}, {"label": "Export"}]
        if stage == "HIL Review":
            return [{"label": "Approve", "primary": True}, {"label": "Risk"}]
        if stage == "Pricing":
            return [{"label": "Review", "primary": True}, {"label": "Bridge"}]
        if stage == "Extracting":
            return [{"label": "Validate"}, {"label": "Pause"}]
        return [{"label": "Monitor"}, {"label": "Details"}]

    out = []
    for r in rows:
        stage = r["pipeline_stage"]
        name = f"{r['rfp_code']} · {r['short_label']}" if r["short_label"] else r["rfp_code"]
        out.append({
            "name":  name,
            "org":   r["org"],
            "model": r["pricing_model"],
            "tcv":   r["tcv_display"],
            "stage": {"label": "HIL Review" if stage == "HIL Review" else stage,
                      "variant": stage_variant.get(stage, "ingest")},
            "hil":   _hil_tag(r["current_hil_level"], r["status"]),
            "actions": _actions_for(stage, r["status"]),
        })
    return out


@router.get("/scenarios")
def scenarios(rfp_code: str | None = None):
    code = rfp_code or _current_rfp_code()

    rfp = query_one(
        "SELECT id, rfp_code, short_label, scenario_assumptions FROM rfps WHERE rfp_code = %s",
        (code,),
    )
    if rfp is None:
        raise HTTPException(status_code=404, detail=f"RFP {code!r} not found")

    scenario_rows = query_all(
        """
        SELECT scenario_type, annual_value_display, period_sub,
               volume_display, volume_factor, margin_pct, sell_rate_display, is_recommended
        FROM pricing_scenarios
        WHERE rfp_id = %s
        ORDER BY CASE scenario_type
                    WHEN 'Conservative' THEN 1
                    WHEN 'Base'         THEN 2
                    WHEN 'Aggressive'   THEN 3
                 END
        """,
        (rfp["id"],),
    )

    def _variant(t: str) -> str:
        return {"Conservative": "conservative", "Base": "base", "Aggressive": "aggressive"}[t]

    def _label(t: str, recommended: bool) -> str:
        return "Base (Recommended)" if recommended else t

    scenarios_payload = [
        {
            "variant":     _variant(s["scenario_type"]),
            "label":       _label(s["scenario_type"], bool(s["is_recommended"])),
            "val":         s["annual_value_display"],
            "sub":         s["period_sub"],
            "recommended": bool(s["is_recommended"]),
            "rows": [
                {"label": "Volume",     "value": s["volume_display"]},
                {"label": "Vol Factor", "value": s["volume_factor"]},
                {"label": "Margin",     "value": s["margin_pct"]},
                {"label": "Sell Rate",  "value": s["sell_rate_display"]},
            ],
        }
        for s in scenario_rows
    ]

    return {
        "rfp_code":    rfp["rfp_code"],
        "rfp_label":   rfp["short_label"],
        "assumptions": rfp["scenario_assumptions"] or "",
        "scenarios":   scenarios_payload,
        "tooltip": {
            "title": "Pricing Scenario Definitions",
            "rows": [
                {"dot": "cons", "title": "Conservative",
                 "body": "Lower volume forecast, higher margin. Safer pricing that protects profitability if demand falls short."},
                {"dot": "base", "title": "Base (Recommended)",
                 "body": "Most-likely volume and balanced margin. Aligned with historical client behaviour and market norms."},
                {"dot": "aggr", "title": "Aggressive",
                 "body": "Higher volume assumed, thinner margin. Competitive price designed to maximize win probability."},
            ],
        },
    }


@router.get("/benchmarks")
def benchmarks(rfp_code: str | None = None):
    code = rfp_code or _current_rfp_code()
    rfp = query_one(
        "SELECT id, benchmark_scope, benchmark_note FROM rfps WHERE rfp_code = %s",
        (code,),
    )
    if rfp is None:
        raise HTTPException(status_code=404, detail=f"RFP {code!r} not found")

    rows = query_all(
        """
        SELECT label, rate_display, bar_width_pct, color_css
        FROM benchmarks
        WHERE rfp_id = %s
        ORDER BY sort_order
        """,
        (rfp["id"],),
    )
    return {
        "intro": rfp["benchmark_scope"] or "",
        "note":  rfp["benchmark_note"] or "",
        "rows": [
            {
                "label": r["label"],
                "val":   r["rate_display"],
                "width": f"{r['bar_width_pct']}%",
                "color": r["color_css"],
            }
            for r in rows
        ],
    }


@router.get("/risks")
def risks(rfp_code: str | None = None):
    code = rfp_code or _current_rfp_code()
    rfp = query_one("SELECT id FROM rfps WHERE rfp_code = %s", (code,))
    if rfp is None:
        raise HTTPException(status_code=404, detail=f"RFP {code!r} not found")

    rows = query_all(
        """
        SELECT severity, description
        FROM contract_risks
        WHERE rfp_id = %s
        ORDER BY sort_order
        """,
        (rfp["id"],),
    )
    return [{"variant": r["severity"], "text": r["description"]} for r in rows]


@router.get("/hil-checkpoints")
def hil_checkpoints(rfp_code: str | None = None):
    code = rfp_code or _current_rfp_code()
    rfp = query_one("SELECT id FROM rfps WHERE rfp_code = %s", (code,))
    if rfp is None:
        raise HTTPException(status_code=404, detail=f"RFP {code!r} not found")

    rows = query_all(
        """
        SELECT hc.level, hc.title, hc.description AS desc, hc.owner_role AS who,
               p.status
        FROM hil_checkpoints hc
        LEFT JOIN rfp_hil_progress p
          ON p.level = hc.level AND p.rfp_id = %s
        ORDER BY hc.level
        """,
        (rfp["id"],),
    )

    status_label = {
        "done":    "✓ Complete",
        "pending": "⏳ Awaiting",
        "waiting": "🔵 Queued",
    }

    return [
        {
            "level": r["level"],
            "title": r["title"],
            "desc":  r["desc"],
            "who":   r["who"],
            "status": {
                "label":   status_label.get(r["status"] or "waiting", "🔵 Queued"),
                "variant": r["status"] or "waiting",
            },
        }
        for r in rows
    ]


@router.get("/winrate")
def winrate(range: str = Query("quarter", pattern="^(week|month|quarter)$")):
    points = query_all(
        """
        SELECT period_label AS x, win_rate_pct AS val
        FROM win_rate_points
        WHERE range_type = %s
        ORDER BY seq
        """,
        (range,),
    )
    insight_rows = query_all(
        """
        SELECT slot, label, value, color_css, header_label, sub_label
        FROM win_rate_insights
        WHERE range_type = %s
        ORDER BY slot
        """,
        (range,),
    )

    if not insight_rows:
        raise HTTPException(status_code=404, detail=f"Unknown range {range!r}")

    return {
        "range":  range,
        "label":  insight_rows[0]["header_label"],
        "sub":    insight_rows[0]["sub_label"],
        "data":   rows_to_dicts(points),
        "insights": [
            {"lbl": r["label"], "val": r["value"], "color": r["color_css"]}
            for r in insight_rows
        ],
    }
