"""Drop and re-create the PostgreSQL schema from ddl.sql + dml.sql.

Reads `DATABASE_URL` from the environment (or .env file in the backend root).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parent.parent
DDL  = ROOT / "db" / "ddl.sql"
DML  = ROOT / "db" / "dml.sql"

load_dotenv(ROOT / ".env")


def _redact(url: str) -> str:
    if "@" in url:
        return url.split("@", 1)[1].split("?", 1)[0]
    return url


def main() -> int:
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if not url:
        print("[init_db] DATABASE_URL not set. "
              "Copy .env.example to .env and paste your Aiven connection string.",
              file=sys.stderr)
        return 1

    for path in (DDL, DML):
        if not path.exists():
            print(f"[init_db] missing: {path}", file=sys.stderr)
            return 1

    print(f"[init_db] connecting to {_redact(url)}")

    try:
        with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                print(f"[init_db] applying {DDL.name}")
                cur.execute(DDL.read_text(encoding="utf-8"))

                print(f"[init_db] applying {DML.name}")
                cur.execute(DML.read_text(encoding="utf-8"))

                cur.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                """)
                tables = [r["table_name"] for r in cur.fetchall()]

                counts: dict[str, int] = {}
                for t in tables:
                    cur.execute(f'SELECT COUNT(*) AS n FROM "{t}"')
                    counts[t] = cur.fetchone()["n"]
            conn.commit()
    except psycopg.Error as exc:
        print(f"[init_db] ERROR: {exc}", file=sys.stderr)
        return 1

    print("[init_db] applied — row counts:")
    for t, n in counts.items():
        print(f"           {t:<22} {n:>4}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
