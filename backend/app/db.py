from __future__ import annotations

import csv
import json
import os
import sqlite3
from collections import defaultdict
from contextlib import contextmanager
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - keeps local SQLite usable before pip install.
    def load_dotenv(*_args, **_kwargs) -> bool:
        return False

try:
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool
except ImportError:  # pragma: no cover - only used when psycopg is not installed.
    dict_row = None
    ConnectionPool = None


ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
CORPUS_OUT = WORKSPACE / "database" / "out"
SQLITE_PATH = Path(os.environ.get("SQLITE_PATH", ROOT / "local.db"))

load_dotenv(ROOT / ".env")

_raw_database_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
DATABASE_URL = (
    _raw_database_url
    if _raw_database_url and "REPLACE_" not in _raw_database_url
    else None
)
USE_POSTGRES = bool(DATABASE_URL) and os.environ.get("DATABASE_MODE", "").lower() != "sqlite"


class _SqlitePool:
    def open(self) -> None:
        _init_sqlite()

    def close(self) -> None:
        return None


if USE_POSTGRES:
    if ConnectionPool is None or dict_row is None:
        raise RuntimeError("psycopg and psycopg-pool are required for PostgreSQL mode.")
    pool = ConnectionPool(
        DATABASE_URL,
        min_size=1,
        max_size=5,
        open=False,
        kwargs={"row_factory": dict_row},
    )
else:
    pool = _SqlitePool()


def open_database() -> None:
    global USE_POSTGRES, pool

    if USE_POSTGRES:
        try:
            pool.open()
            pool.wait(timeout=5)
            _load_dataset_postgres()
            return
        except Exception:
            pool.close()
            USE_POSTGRES = False
            pool = _SqlitePool()

    pool.open()


def close_database() -> None:
    pool.close()


def backend_name() -> str:
    return "postgresql" if USE_POSTGRES else "sqlite"


SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS rfps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfp_code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    short_label TEXT,
    client_id INTEGER NOT NULL REFERENCES clients(id),
    category TEXT NOT NULL,
    description TEXT,
    tcv_base INTEGER NOT NULL,
    pricing_model TEXT NOT NULL,
    scenario_used TEXT,
    renewal_date TEXT,
    submitted_date TEXT,
    duration TEXT,
    locale TEXT,
    win_probability INTEGER,
    risk_level TEXT,
    hil_stage TEXT,
    status TEXT NOT NULL,
    pipeline_stage TEXT,
    current_hil_level INTEGER,
    scenario_assumptions TEXT,
    benchmark_scope TEXT,
    benchmark_note TEXT,
    tcv_display TEXT,
    active_in_pipeline INTEGER NOT NULL DEFAULT 0,
    active_pipeline_rank INTEGER,
    is_current INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_rfps_client ON rfps(client_id);
CREATE INDEX IF NOT EXISTS idx_rfps_status ON rfps(status);
CREATE INDEX IF NOT EXISTS idx_rfps_category ON rfps(category);
CREATE INDEX IF NOT EXISTS idx_rfps_pricing_model ON rfps(pricing_model);
CREATE INDEX IF NOT EXISTS idx_rfps_pipeline_stage ON rfps(pipeline_stage);

CREATE TABLE IF NOT EXISTS pricing_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfp_id INTEGER NOT NULL REFERENCES rfps(id) ON DELETE CASCADE,
    scenario_type TEXT NOT NULL,
    annual_value_display TEXT NOT NULL,
    period_sub TEXT NOT NULL,
    volume_display TEXT NOT NULL,
    volume_factor TEXT NOT NULL,
    margin_pct TEXT NOT NULL,
    sell_rate_display TEXT NOT NULL,
    is_recommended INTEGER NOT NULL DEFAULT 0,
    UNIQUE (rfp_id, scenario_type)
);

CREATE TABLE IF NOT EXISTS hil_checkpoints (
    level INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    owner_role TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rfp_hil_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfp_id INTEGER NOT NULL REFERENCES rfps(id) ON DELETE CASCADE,
    level INTEGER NOT NULL REFERENCES hil_checkpoints(level),
    status TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (rfp_id, level)
);

CREATE TABLE IF NOT EXISTS benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfp_id INTEGER NOT NULL REFERENCES rfps(id) ON DELETE CASCADE,
    label TEXT NOT NULL,
    rate_display TEXT NOT NULL,
    bar_width_pct INTEGER NOT NULL,
    color_css TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS contract_risks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfp_id INTEGER NOT NULL REFERENCES rfps(id) ON DELETE CASCADE,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rfp_id INTEGER NOT NULL REFERENCES rfps(id) ON DELETE CASCADE,
    level INTEGER NOT NULL REFERENCES hil_checkpoints(level),
    title TEXT NOT NULL,
    meta TEXT,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actioned_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);

CREATE TABLE IF NOT EXISTS pricing_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    label TEXT NOT NULL,
    description TEXT NOT NULL,
    kind TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS win_rate_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    range_type TEXT NOT NULL,
    period_label TEXT NOT NULL,
    win_rate_pct INTEGER NOT NULL,
    seq INTEGER NOT NULL,
    UNIQUE (range_type, seq)
);

CREATE TABLE IF NOT EXISTS win_rate_insights (
    range_type TEXT NOT NULL,
    slot INTEGER NOT NULL,
    label TEXT NOT NULL,
    value TEXT NOT NULL,
    color_css TEXT,
    header_label TEXT NOT NULL,
    sub_label TEXT NOT NULL,
    PRIMARY KEY (range_type, slot)
);

CREATE TABLE IF NOT EXISTS activity_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    variant TEXT NOT NULL UNIQUE,
    icon TEXT NOT NULL,
    value TEXT NOT NULL,
    label TEXT NOT NULL,
    trend_dir TEXT NOT NULL,
    trend_text TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS top_deal_today (
    id INTEGER PRIMARY KEY,
    summary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS accuracy_buckets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bucket_label TEXT NOT NULL UNIQUE,
    deal_count INTEGER NOT NULL,
    in_sweet_spot INTEGER NOT NULL DEFAULT 0,
    seq INTEGER NOT NULL
);
"""


def _sqlite_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _translate_sql(sql: str) -> str:
    if USE_POSTGRES:
        return sql
    return sql.replace("%s", "?").replace("ILIKE", "LIKE")


class _CursorProxy:
    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._cursor.close()

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    def execute(self, sql: str, params: tuple | list | dict = ()):
        self._cursor.execute(_translate_sql(sql), params)
        return self

    def fetchone(self) -> dict | None:
        row = self._cursor.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self) -> list[dict]:
        return [dict(r) for r in self._cursor.fetchall()]


class _ConnProxy:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self._conn.commit()
        self._conn.close()

    def cursor(self) -> _CursorProxy:
        return _CursorProxy(self._conn.cursor())

    def execute(self, sql: str, params: tuple | list | dict = ()) -> _CursorProxy:
        cursor = self.cursor()
        cursor.execute(sql, params)
        return cursor

    def commit(self) -> None:
        self._conn.commit()


@contextmanager
def get_conn():
    if USE_POSTGRES:
        with pool.connection() as conn:
            yield conn
    else:
        with _ConnProxy(_sqlite_conn()) as conn:
            yield conn


def query_all(sql: str, params: tuple | dict = ()) -> list[dict]:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def query_one(sql: str, params: tuple | dict = ()) -> dict | None:
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()


def row_to_dict(row: dict | None) -> dict | None:
    return row


def rows_to_dicts(rows: list[dict]) -> list[dict]:
    return list(rows)


def _read_csv(name: str) -> list[dict]:
    path = CORPUS_OUT / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _money_inr(amount: int) -> str:
    return f"₹{amount:,}"


def _category(row: dict, extracted: dict | None) -> str:
    industry = (row.get("industry") or "").lower()
    service_types = []
    if extracted and extracted.get("service_types"):
        try:
            service_types = json.loads(extracted["service_types"])
        except json.JSONDecodeError:
            service_types = []
    joined = " ".join(service_types).lower()
    if "translation" in joined:
        return "Translation"
    if "interpret" in joined:
        return "Interpretation"
    if "support" in joined or "customer" in joined:
        return "Call Center"
    if "technology" in industry or "engineering" in joined:
        return "IT Services"
    return "BPO"


def _pricing_model(value: str) -> str:
    return {
        "RETAINER": "Annual Retainer",
        "TIERED": "Hybrid",
        "FIXED_FEE": "Fixed Fee",
        "PER_UNIT": "Per Word",
        "TIME_AND_MATERIALS": "Per Hour",
        "HYBRID": "Hybrid",
        "PMPM": "PMPM",
    }.get((value or "").upper(), "Hybrid")


def _status(value: str) -> str:
    return {
        "UPLOADED": "Active",
        "EXTRACTED": "Active",
        "PRICED": "Priced",
        "COMPLETED": "Awarded",
        "ARCHIVED": "Archived",
    }.get((value or "").upper(), "Active")


def _risk(confidence: str | None) -> str:
    try:
        score = float(confidence or 0.75)
    except ValueError:
        score = 0.75
    if score >= 0.9:
        return "Low"
    if score >= 0.82:
        return "Medium"
    return "High"


def _duration(extracted: dict | None) -> str:
    if not extracted:
        return "1 year"
    try:
        terms = json.loads(extracted.get("commercial_terms") or "{}")
        months = int(terms.get("duration_months") or 12)
    except (TypeError, ValueError, json.JSONDecodeError):
        months = 12
    return f"{max(1, round(months / 12))} year{'s' if months != 12 else ''}"


def _locales(extracted: dict | None) -> str:
    if not extracted:
        return "en-US"
    try:
        values = json.loads(extracted.get("locales") or "[]")
    except json.JSONDecodeError:
        values = []
    return ", ".join(values[:4]) or "en-US"


def _load_dataset(conn: sqlite3.Connection) -> None:
    if os.environ.get("LOAD_CORPUS", "true").lower() == "false":
        return
    if not CORPUS_OUT.exists():
        return

    already = conn.execute("SELECT COUNT(*) FROM rfps WHERE rfp_code LIKE 'DS-%'").fetchone()[0]
    if already:
        conn.execute("UPDATE rfps SET pipeline_stage = NULL, active_in_pipeline = 0 WHERE rfp_code LIKE 'DS-%'")
        conn.commit()
        return

    extracted_by_rfp = {r["rfp_id"]: r for r in _read_csv("extracted_data.csv")}
    deals_by_id = {r["deal_id"]: r for r in _read_csv("deals.csv")}
    totals_by_rfp: dict[str, float] = defaultdict(float)
    for row in _read_csv("pricing_output.csv"):
        deal = deals_by_id.get(row.get("deal_id"))
        if not deal:
            continue
        try:
            totals_by_rfp[deal["rfp_id"]] += float(row.get("line_total") or 0)
        except ValueError:
            continue

    rfps = _read_csv("rfp.csv")
    if not rfps:
        return

    scenarios = ["Conservative", "Base", "Aggressive"]

    for idx, row in enumerate(rfps, start=1):
        client = row.get("client_name") or "Unknown Client"
        conn.execute("INSERT OR IGNORE INTO clients (name) VALUES (?)", (client,))
        client_id = conn.execute("SELECT id FROM clients WHERE name = ?", (client,)).fetchone()[0]

        extracted = extracted_by_rfp.get(row.get("rfp_id"))
        total_usd = totals_by_rfp.get(row.get("rfp_id"), 0)
        tcv_base = max(100_000, round(total_usd * 83))
        status = _status(row.get("status", ""))
        stage = None
        level = 1
        scenario = scenarios[idx % len(scenarios)]
        risk = _risk(extracted.get("confidence_score") if extracted else None)
        model = _pricing_model(extracted.get("pricing_model") if extracted else "")
        uploaded = (row.get("uploaded_at") or "")[:10]
        display_name = Path(row.get("file_name") or f"RFP {idx}").stem.replace("_", " ")

        conn.execute(
            """
            INSERT OR IGNORE INTO rfps
              (rfp_code, name, short_label, client_id, category, description,
               tcv_base, pricing_model, scenario_used, renewal_date, submitted_date,
               duration, locale, win_probability, risk_level, hil_stage,
               status, pipeline_stage, current_hil_level,
               scenario_assumptions, benchmark_scope, benchmark_note,
               tcv_display, active_in_pipeline, active_pipeline_rank, is_current)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"DS-{idx:05d}",
                display_name,
                display_name[:24],
                client_id,
                _category(row, extracted),
                f"{row.get('industry', 'Enterprise')} pricing request imported from database/out.",
                tcv_base,
                model,
                scenario,
                "",
                uploaded,
                _duration(extracted),
                _locales(extracted),
                min(96, max(35, round((float(extracted.get("confidence_score", 0.78)) if extracted else 0.78) * 100))),
                risk,
                f"L{level}",
                status,
                stage,
                level,
                "",
                "",
                "",
                _money_inr(tcv_base),
                0,
                None,
                0,
            ),
        )

    conn.commit()


def _dataset_rows() -> list[tuple]:
    extracted_by_rfp = {r["rfp_id"]: r for r in _read_csv("extracted_data.csv")}
    deals_by_id = {r["deal_id"]: r for r in _read_csv("deals.csv")}
    totals_by_rfp: dict[str, float] = defaultdict(float)
    for row in _read_csv("pricing_output.csv"):
        deal = deals_by_id.get(row.get("deal_id"))
        if not deal:
            continue
        try:
            totals_by_rfp[deal["rfp_id"]] += float(row.get("line_total") or 0)
        except ValueError:
            continue

    rows = []
    scenarios = ["Conservative", "Base", "Aggressive"]
    for idx, row in enumerate(_read_csv("rfp.csv"), start=1):
        extracted = extracted_by_rfp.get(row.get("rfp_id"))
        total_usd = totals_by_rfp.get(row.get("rfp_id"), 0)
        tcv_base = max(100_000, round(total_usd * 83))
        status = _status(row.get("status", ""))
        level = 1
        uploaded = (row.get("uploaded_at") or "")[:10]
        display_name = Path(row.get("file_name") or f"RFP {idx}").stem.replace("_", " ")
        confidence = float(extracted.get("confidence_score", 0.78)) if extracted else 0.78

        rows.append((
            row.get("client_name") or "Unknown Client",
            f"DS-{idx:05d}",
            display_name,
            display_name[:24],
            _category(row, extracted),
            f"{row.get('industry', 'Enterprise')} pricing request imported from database/out.",
            tcv_base,
            _pricing_model(extracted.get("pricing_model") if extracted else ""),
            scenarios[idx % len(scenarios)],
            "",
            uploaded,
            _duration(extracted),
            _locales(extracted),
            min(96, max(35, round(confidence * 100))),
            _risk(extracted.get("confidence_score") if extracted else None),
            f"L{level}",
            status,
            None,
            level,
            "",
            "",
            "",
            _money_inr(tcv_base),
            0,
            None,
            0,
        ))
    return rows


def _load_dataset_postgres() -> None:
    if os.environ.get("LOAD_CORPUS", "true").lower() == "false" or not CORPUS_OUT.exists():
        return

    with pool.connection() as conn:
        already = conn.execute("SELECT COUNT(*) AS n FROM rfps WHERE rfp_code LIKE 'DS-%'").fetchone()["n"]
        if already:
            conn.execute(
                "UPDATE rfps SET pipeline_stage = NULL, active_in_pipeline = FALSE WHERE rfp_code LIKE 'DS-%'"
            )
            conn.commit()
            return

        for row in _dataset_rows():
            client_name = row[0]
            conn.execute("INSERT INTO clients (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (client_name,))
            client_id = conn.execute("SELECT id FROM clients WHERE name = %s", (client_name,)).fetchone()["id"]
            conn.execute(
                """
                INSERT INTO rfps
                  (rfp_code, name, short_label, client_id, category, description,
                   tcv_base, pricing_model, scenario_used, renewal_date, submitted_date,
                   duration, locale, win_probability, risk_level, hil_stage,
                   status, pipeline_stage, current_hil_level,
                   scenario_assumptions, benchmark_scope, benchmark_note,
                   tcv_display, active_in_pipeline, active_pipeline_rank, is_current)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (rfp_code) DO NOTHING
                """,
                (row[1], row[2], row[3], client_id, *row[4:]),
            )
        conn.commit()


def _init_sqlite() -> None:
    SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
    should_seed = not SQLITE_PATH.exists()
    with _sqlite_conn() as conn:
        conn.executescript(SQLITE_SCHEMA)
        if should_seed:
            dml = (ROOT / "db" / "dml.sql").read_text(encoding="utf-8")
            conn.executescript(dml)
        _load_dataset(conn)
        conn.commit()
