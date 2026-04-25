# Centific Pricing Intelligence

Centific Pricing Intelligence is a full-stack workspace with three top-level parts:

- `frontend` - React/Vite application.
- `backend` - FastAPI service and API/database wiring.
- `database` - synthetic CSV corpus and data generation utilities.

## Run Locally

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Start the frontend:

```powershell
cd frontend
npm run dev
```

Open http://localhost:5173. API docs are available at http://localhost:8000/docs.

## Run with Docker

The easiest way to run the entire stack is using Docker Compose:

```powershell
docker compose up -d
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Database

The backend uses PostgreSQL when `DATABASE_URL` is configured and reachable. By default, it uses a local SQLite database at `backend/local.db` which is populated from the synthetic data in `database/out`.
