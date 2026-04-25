from fastapi import APIRouter, HTTPException, Query

from ..db import query_all, query_one

router = APIRouter(prefix="/api/corpus", tags=["corpus"])


CORPUS_COLUMNS = [
    {"key": "id",          "label": "RFP ID",        "sortable": True,  "defaultOn": True},
    {"key": "name",        "label": "Name",          "sortable": True,  "defaultOn": True},
    {"key": "status",      "label": "Status",        "sortable": True,  "defaultOn": True},
    {"key": "client",      "label": "Client Org",    "sortable": True,  "defaultOn": True},
    {"key": "category",    "label": "Category",      "sortable": True,  "defaultOn": True},
    {"key": "description", "label": "Description",   "sortable": False, "defaultOn": False},
    {"key": "tcv",         "label": "TCV",           "sortable": True,  "defaultOn": True},
    {"key": "model",       "label": "Pricing Model", "sortable": True,  "defaultOn": False},
    {"key": "renewal",     "label": "Renewal",       "sortable": False, "defaultOn": False},
    {"key": "scenario",    "label": "Scenario",      "sortable": True,  "defaultOn": False},
    {"key": "submitted",   "label": "Submitted",     "sortable": False, "defaultOn": False},
    {"key": "duration",    "label": "Duration",      "sortable": False, "defaultOn": False},
    {"key": "locale",      "label": "Locale",        "sortable": False, "defaultOn": False},
    {"key": "winprob",     "label": "Win %",         "sortable": True,  "defaultOn": True},
    {"key": "risk",        "label": "Risk",          "sortable": True,  "defaultOn": True},
    {"key": "hil",         "label": "HIL Stage",     "sortable": False, "defaultOn": False},
]

FILTER_OPTIONS = {
    "status":   ["Active", "Priced", "Awarded", "Won", "Lost", "Archived"],
    "category": ["Call Center", "Translation", "IT Services", "BPO", "Interpretation"],
    "model":    ["Per Word", "Per Hour", "Annual Retainer", "Fixed Fee", "Hybrid", "Per Claim", "PMPM"],
    "risk":     ["Low", "Medium", "High"],
}

SORT_COLUMN_MAP = {
    "id":       "r.rfp_code",
    "name":     "r.name",
    "status":   "r.status",
    "client":   "c.name",
    "category": "r.category",
    "tcv":      "r.tcv_base",
    "model":    "r.pricing_model",
    "scenario": "r.scenario_used",
    "winprob":  "r.win_probability",
    "risk":     "r.risk_level",
}


def _row_payload(r) -> dict:
    return {
        "id":          r["rfp_code"],
        "name":        r["name"],
        "status":      r["status"],
        "client":      r["client"],
        "category":    r["category"],
        "description": r["description"],
        "tcv":         r["tcv_base"],
        "model":       r["pricing_model"],
        "renewal":     r["renewal_date"] or "—",
        "scenario":    r["scenario_used"],
        "submitted":   r["submitted_date"],
        "duration":    r["duration"],
        "locale":      r["locale"],
        "winprob":     r["win_probability"],
        "risk":        r["risk_level"],
        "hil":         r["hil_stage"],
    }


@router.get("/meta")
def meta():
    return {"columns": CORPUS_COLUMNS, "filterOptions": FILTER_OPTIONS}


@router.get("")
def list_corpus(
    search:   str | None = None,
    status:   str | None = None,
    category: str | None = None,
    model:    str | None = None,
    risk:     str | None = None,
    sort:     str | None = Query(None, description="Column key to sort by"),
    dir:      str = Query("asc", pattern="^(asc|desc)$"),
):
    clauses = []
    params: list = []

    if search:
        like = f"%{search}%"
        clauses.append(
            "(r.rfp_code ILIKE %s OR r.name ILIKE %s OR c.name ILIKE %s OR r.description ILIKE %s)"
        )
        params.extend([like, like, like, like])
    if status:
        clauses.append("r.status = %s")
        params.append(status)
    if category:
        clauses.append("r.category = %s")
        params.append(category)
    if model:
        clauses.append("r.pricing_model = %s")
        params.append(model)
    if risk:
        clauses.append("r.risk_level = %s")
        params.append(risk)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    order = ""
    if sort and sort in SORT_COLUMN_MAP:
        order = f"ORDER BY {SORT_COLUMN_MAP[sort]} {dir.upper()}"

    sql = f"""
        SELECT r.rfp_code, r.name, r.status, c.name AS client, r.category, r.description,
               r.tcv_base, r.pricing_model, r.renewal_date, r.scenario_used,
               r.submitted_date, r.duration, r.locale,
               r.win_probability, r.risk_level, r.hil_stage
        FROM rfps r
        JOIN clients c ON c.id = r.client_id
        {where}
        {order}
    """
    rows = query_all(sql, tuple(params))
    return {"count": len(rows), "rows": [_row_payload(r) for r in rows]}


@router.get("/{rfp_code}")
def get_one(rfp_code: str):
    row = query_one(
        """
        SELECT r.rfp_code, r.name, r.status, c.name AS client, r.category, r.description,
               r.tcv_base, r.pricing_model, r.renewal_date, r.scenario_used,
               r.submitted_date, r.duration, r.locale,
               r.win_probability, r.risk_level, r.hil_stage
        FROM rfps r
        JOIN clients c ON c.id = r.client_id
        WHERE r.rfp_code = %s
        """,
        (rfp_code,),
    )
    if row is None:
        raise HTTPException(status_code=404, detail=f"RFP {rfp_code!r} not found")
    return _row_payload(row)
