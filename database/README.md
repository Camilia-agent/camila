# Centific Pricing Intelligence Database

This folder contains the synthetic pricing corpus used by the backend.

- `out/` contains generated CSV files.
- `generate.py` creates or extends the dataset.
- `validate.py` checks schema consistency.
- `dataset_stats.py` reports corpus statistics.

The backend imports this corpus automatically from `database/out` into
`backend/local.db` when running in SQLite mode, and can also load it into
PostgreSQL when `DATABASE_URL` is reachable.
