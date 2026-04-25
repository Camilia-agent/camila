from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone

from ..db import get_conn, query_all

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.get("")
def list_pending():
    rows = query_all(
        """
        SELECT a.id, a.level, a.title, a.meta
        FROM approvals a
        WHERE a.status = 'pending'
        ORDER BY a.level, a.created_at
        """
    )
    return [
        {"id": r["id"], "level": r["level"], "title": r["title"], "meta": r["meta"]}
        for r in rows
    ]


@router.post("/{approval_id}/approve")
def approve(approval_id: int):
    return _set_status(approval_id, "approved")


@router.post("/{approval_id}/reject")
def reject(approval_id: int):
    return _set_status(approval_id, "rejected")


def _set_status(approval_id: int, status: str) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE approvals SET status = %s, actioned_at = %s WHERE id = %s AND status = 'pending'",
            (status, datetime.now(timezone.utc), approval_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404,
                                detail=f"Approval {approval_id} not found or already actioned")
    return {"id": approval_id, "status": status}
