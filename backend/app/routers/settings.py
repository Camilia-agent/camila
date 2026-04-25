from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..db import get_conn, query_all, query_one

router = APIRouter(prefix="/api/settings", tags=["settings"])


SETTINGS_NAV = [
    {"id": "pricing",       "label": "⚙️ Pricing Defaults"},
    {"id": "tools",         "label": "🔧 Tool Configuration"},
    {"id": "access",        "label": "🔐 Access & Permissions"},
    {"id": "integrations",  "label": "🔌 Integrations"},
    {"id": "notifications", "label": "📧 Notifications"},
    {"id": "audit",         "label": "📊 Audit Log Retention"},
]


class UpdateValue(BaseModel):
    value: str


@router.get("/pricing-defaults")
def pricing_defaults():
    rows = query_all(
        "SELECT key, value, label, description, kind FROM pricing_settings ORDER BY sort_order"
    )

    def _control(kind: str, value: str) -> dict:
        if kind == "toggle":
            return {"kind": "toggle", "defaultValue": value.lower() == "true"}
        if kind == "input_wide":
            return {"kind": "input", "defaultValue": value, "wide": True}
        return {"kind": "input", "defaultValue": value}

    return {
        "nav": SETTINGS_NAV,
        "rows": [
            {
                "id":      r["key"],
                "h4":      r["label"],
                "p":       r["description"],
                "control": _control(r["kind"], r["value"]),
            }
            for r in rows
        ],
    }


@router.put("/pricing-defaults/{key}")
def update_setting(key: str, body: UpdateValue):
    existing = query_one("SELECT key FROM pricing_settings WHERE key = %s", (key,))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Setting {key!r} not found")

    with get_conn() as conn:
        conn.execute("UPDATE pricing_settings SET value = %s WHERE key = %s", (body.value, key))
        conn.commit()
    return {"key": key, "value": body.value}
