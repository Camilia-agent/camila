# Database Design â€” Centific Pricing Intelligence

**Engine:** PostgreSQL 14+ or local SQLite fallback
**Hosting:** Aiven PostgreSQL in cloud mode, `backend/local.db` in local mode
**Connection:** via `DATABASE_URL` env var (SSL required)
**Schema file:** [../db/ddl.sql](../db/ddl.sql)
**Seed file:**   [../db/dml.sql](../db/dml.sql)

---

## 1. Purpose

The schema backs the Centific Pricing Intelligence frontend. It has
to serve seven views â€” Dashboard, Pipeline kanban, Analytics, HIL Approvals,
Settings, Corpus Library, Search, and Help.

Design goals, in order:

1. **Fidelity with the frontend.** Every value rendered in
   `API-backed frontend views` must be derivable from the database, either by direct
   lookup or by a simple aggregation.
2. **Normalization where it pays off.** Client names, pricing-model labels,
   and HIL checkpoint metadata are reused across many rows â€” they live in
   lookup tables.
3. **Denormalization where it saves work.** Display-formatted strings (e.g.
   `tcv_display = 'â‚¹16,84,620'`, `annual_value_display = 'â‚¹3.42L'`) are stored
   next to their numeric counterparts so the frontend doesn't have to re-implement
   Indian-format rupee logic.
4. **No over-engineering.** Snapshot-style data (today's activity tiles,
   win-rate time series, accuracy histogram) is stored verbatim rather than
   reconstructed from a transactional ledger. The source-of-truth for those
   aggregates lives outside the app.

---

## 2. Entity-relationship overview

```
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚ clients  â”‚
                     â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜
                          â”‚ 1
                          â”‚
                          â”‚ âˆž
                     â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”       1   âˆž  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚          â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚ pricing_scenarios  â”‚
                     â”‚          â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚          â”‚       1   âˆž  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚          â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚ benchmarks         â”‚
                     â”‚          â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚  rfps    â”‚       1   âˆž  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚          â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚ contract_risks     â”‚
                     â”‚          â”‚              â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚          â”‚       1   âˆž  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚          â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–ºâ”‚ rfp_hil_progress   â”‚
                     â”‚          â”‚              â””â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚          â”‚       1   âˆž     â”‚ âˆž   1
                     â”‚          â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”˜           â”‚  â”‚ hil_checkpoints   â”‚
                          â”‚ 1               â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                          â”‚                 â”‚           â”‚ 1
                          â”‚ âˆž               â”‚           â”‚
                     â”Œâ”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”           â”‚           â”‚ âˆž
                     â”‚ approvalsâ”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â”€â”€â”€â”€â”€â”€â”€â”€â–¼
                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜                (approvals.level â†’ hil_checkpoints.level)
```

**Standalone tables** (not joined to `rfps`): `pricing_settings`,
`win_rate_points`, `win_rate_insights`, `activity_snapshot`, `top_deal_today`,
`accuracy_buckets`. They hold config or precomputed aggregate data.

---

## 3. Tables

### 3.1 `clients`

Client organizations issuing RFPs.

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` (IDENTITY) | PK, auto-generated |
| `name` | `TEXT UNIQUE` | e.g. `'City of Tucker, GA'` |

### 3.2 `rfps`  *(central table)*

Each row is one RFP. Drives almost every page.

**Identity / classification:**
`rfp_code` (public ID), `name`, `short_label`, `client_id`, `category`,
`description`.

**Commercial:**
`tcv_base BIGINT` (INR in integer rupees), `tcv_display TEXT` (formatted),
`pricing_model`, `scenario_used`, `renewal_date`, `submitted_date`,
`duration`, `locale`.

**Scoring / workflow:**
`win_probability`, `risk_level`, `hil_stage`, `status`, `pipeline_stage`,
`current_hil_level`.

**Dashboard-scoped text:**
`scenario_assumptions`, `benchmark_scope`, `benchmark_note` â€” populated only
for the "current" RFP surfaced on the dashboard (`25PPA-003` in the seed).

**Display flags (BOOLEAN):**
- `active_in_pipeline` / `active_pipeline_rank` â€” selects & orders the 5 rows
  shown in the Dashboard's *Active RFP Pipeline* table.
- `is_current` â€” single-row flag picking which RFP's scenarios/benchmarks/risks
  appear on the dashboard. Exactly one row has this = `TRUE`.

**Timestamps:** `created_at TIMESTAMPTZ DEFAULT NOW()`.

Indexes on `client_id`, `status`, `category`, `pricing_model`, `pipeline_stage`
(each is a filter / group-by target).

### 3.3 `pricing_scenarios`

Three rows per RFP (Conservative / Base / Aggressive). Columns are almost all
display-formatted strings (`annual_value_display='â‚¹3.42L'`, `volume_factor='Ã—0.90'`,
â€¦) because the source values the frontend uses are textual.

Uniqueness on `(rfp_id, scenario_type)`.

### 3.4 `hil_checkpoints`

Master reference â€” exactly five rows (levels 1â€“5). Holds the title, description,
and owner role for each HIL stage. Cheap to join and gives a single point of
truth for any copy changes.

### 3.5 `rfp_hil_progress`

Per-RFP status at each of the five checkpoint levels: `done`, `pending`,
or `waiting`. Uniqueness on `(rfp_id, level)`.

### 3.6 `benchmarks`

Historical-rate bars (5 rows for the current RFP in the seed). Stores both
the bar width percentage and the colour CSS token. Ordering via `sort_order`.

### 3.7 `contract_risks`

Low/med/high risk items for a given RFP.

### 3.8 `approvals`

Pending HIL approval inbox. `level` FKs to `hil_checkpoints`.
Status starts at `pending` and moves to `approved` / `rejected` once actioned
(`actioned_at TIMESTAMPTZ`).

### 3.9 `pricing_settings`

Key-value configuration for the Settings page's *Pricing Defaults* section.
Each row carries its own label / description / widget kind so the UI can be
rendered generically from a single query.

### 3.10 `win_rate_points`

Win-rate time series, three ranges (`week` / `month` / `quarter`).

### 3.11 `win_rate_insights`

The three small tiles rendered under the win-rate chart. Stored per range
rather than computed â€” their labels differ ("Best Week" vs. "Best Quarter")
and the forecast values are editorial.

### 3.12 `activity_snapshot`

Today's 4 activity tiles. A snapshot table.

### 3.13 `top_deal_today`

Single-row table (PK pinned to `id = 1`) for the gold "ðŸ† Today's Top Deal"
banner.

### 3.14 `accuracy_buckets`

Pre-bucketed histogram for *Pricing Accuracy Distribution* â€” nine buckets
(-10% through +10% in 2.5-point steps) with `in_sweet_spot BOOLEAN` marking
the Â±5% band.

---

## 4. Derived vs. stored data

| Frontend surface | Source |
|---|---|
| Dashboard KPIs (RFP count, total TCV, win rate, pending approvals) | **Computed** aggregations over `rfps` + `approvals` + `win_rate_points`. |
| Active-pipeline table | **Stored flag**: `rfps.active_in_pipeline = TRUE ORDER BY active_pipeline_rank`. |
| Pipeline kanban | **Computed**: `GROUP BY pipeline_stage`. |
| Pricing Model Distribution (donut) | **Computed**: `GROUP BY pricing_model`, bucketed into 4 display groups in the API layer. |
| TCV by Category (bars) | **Computed**: `SUM(tcv_base) GROUP BY category`. |
| Win-rate chart (all 3 ranges) | **Stored**. |
| Accuracy distribution | **Stored**. |
| Activity tiles | **Stored snapshot**. |
| Corpus | **Stored** (one row = one RFP). |

Rule of thumb: anything that's a function of the RFP corpus is computed;
anything whose source lives outside our schema (event streams, external KPIs)
is stored as a snapshot.

---

## 5. PostgreSQL-specific choices

- **Identity columns over `SERIAL`.** The DDL uses
  `INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY` (SQL:2003) rather than
  `SERIAL`. It's the modern idiom and doesn't expose an implicit sequence.
- **`BOOLEAN` not `INTEGER` for flags.** Every 0/1 flag from the SQLite version
  (`active_in_pipeline`, `is_current`, `is_recommended`, `in_sweet_spot`) is now
  a proper `BOOLEAN`.
- **`TIMESTAMPTZ` for all timestamps.** Stored in UTC, rendered in the client's
  timezone. Defaulted via `NOW()`.
- **`BIGINT` for money.** `tcv_base` holds integer rupees; a single SAP contract
  already hits â‚¹4.5 Cr = 45 000 000, comfortably inside INT, but BIGINT keeps
  headroom and matches the common money-in-smallest-unit idiom.
- **`ON DELETE CASCADE` on child FKs** (`pricing_scenarios`, `benchmarks`,
  `contract_risks`, `approvals`, `rfp_hil_progress`) so deleting an RFP removes
  its satellite rows. `rfps.client_id` uses `ON DELETE RESTRICT` â€” deleting a
  client with live RFPs is an error.
- **No `PRAGMA foreign_keys = ON`.** PostgreSQL enforces FKs unconditionally.

---

## 6. Constraints and invariants

- All enum-like columns use `CHECK (â€¦ IN (â€¦))` constraints (`status`,
  `risk_level`, `severity`, `scenario_type`, `range_type`, `kind`, â€¦).
- `pricing_scenarios.rfp_id + scenario_type` is unique â€” one scenario per
  type per RFP.
- `rfp_hil_progress.rfp_id + level` is unique â€” one status row per checkpoint
  per RFP.
- `top_deal_today.id CHECK (id = 1)` pins the table to at most one row.
- `bar_width_pct`, `win_rate_pct`, `win_probability` are all range-checked
  to `0..100`.
- `current_hil_level` is range-checked to `0..5`.
- Exactly one `rfps` row should have `is_current = TRUE`; this is a soft
  convention (not enforced) but the init script seeds it that way.

---

## 7. Re-seeding

```bash
# one-time setup
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# copy .env.example â†’ .env and paste the Aiven DATABASE_URL
# then:
python scripts\init_db.py
```

The script connects using `DATABASE_URL`, drops every table via the DDL's
`DROP TABLE IF EXISTS â€¦ CASCADE` stanza, re-runs the schema, then applies the
DML inside a single transaction. Both files are idempotent â€” re-running is
safe (and wipes any local edits).

---

## 8. Extending the schema

| Want toâ€¦ | Change |
|---|---|
| Track approval actions (who, when) | Add `approvals.actioned_by` (FK to a future `users` table) alongside the existing `actioned_at`. |
| Historize settings changes | Add `pricing_settings_history (key, value, changed_at, changed_by)` and write on update. |
| Model pipeline transitions | Add `pipeline_transitions (rfp_id, from_stage, to_stage, at, by)` â€” lets you reconstruct the kanban over time rather than using the current point-in-time `pipeline_stage` column. |
| Replace snapshot tables with derived data | Replace `activity_snapshot` with a proper `activity_log` event stream and compute today's tiles on the fly. |
| Use proper `DATE` types | Migrate `renewal_date` / `submitted_date` from TEXT to `DATE NULL`; adapt the corpus API to emit `'â€”'` for nulls. |
