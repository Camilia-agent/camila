# Centific Pricing Intelligence Backend

FastAPI backend for the Centific Pricing Intelligence frontend in `../frontend/`.

## Database Modes

The API now works in both cloud and local development:

- PostgreSQL / Aiven when `DATABASE_URL` points to a reachable service.
- Local SQLite fallback at `backend/local.db` when PostgreSQL is missing or unavailable.

SQLite mode auto-creates the schema, applies the curated seed data from `db/dml.sql`,
and imports the CSV corpus from `../database/out/*.csv` into `/api/corpus`.

Force local mode even when `.env` has a PostgreSQL URL:

```powershell
$env:DATABASE_MODE='sqlite'
python -m uvicorn app.main:app --reload --port 8000
```

## Setup

```powershell
python -m pip install -r requirements.txt

# Optional: only needed for PostgreSQL mode
copy .env.example .env
python scripts\init_db.py
```

## Run

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- Health: http://localhost:8000/api/health
- Frontend dev server: run `npm run dev` in `../frontend`

The health response includes the active backend:

```json
{"status":"ok","database":"sqlite"}
```

## Data Flow

- `db/ddl.sql` and `db/dml.sql` define the curated dashboard, approvals, settings,
  analytics, benchmark, and HIL data.
- `../database/out/rfp.csv`, `extracted_data.csv`, `deals.csv`, and
  `pricing_output.csv` are linked into the local corpus library.
- The imported dataset is searchable/filterable through the existing
  `/api/corpus` endpoints.

## Endpoints

```text
GET  /api/health
GET  /api/dashboard/kpis
GET  /api/dashboard/pipeline
GET  /api/dashboard/scenarios
GET  /api/dashboard/benchmarks
GET  /api/dashboard/risks
GET  /api/dashboard/hil-checkpoints
GET  /api/dashboard/winrate
GET  /api/pipeline/kanban
GET  /api/analytics/model-distribution
GET  /api/analytics/tcv-by-category
GET  /api/analytics/activity
GET  /api/analytics/accuracy
GET  /api/approvals
POST /api/approvals/{id}/approve
POST /api/approvals/{id}/reject
GET  /api/settings/pricing-defaults
PUT  /api/settings/pricing-defaults/{key}
GET  /api/corpus/meta
GET  /api/corpus
GET  /api/corpus/{rfp_code}
GET  /api/weather
```
