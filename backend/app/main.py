import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db
from .routers import analytics, approvals, corpus, dashboard, pipeline, settings, weather


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.open_database()
    yield
    db.close_database()


app = FastAPI(
    title="Centific Pricing Intelligence API",
    version="0.1.0",
    description="Backend for the Centific Pricing Intelligence platform.",
    lifespan=lifespan,
)

_raw_origins = os.environ.get(
    "ALLOW_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(pipeline.router)
app.include_router(analytics.router)
app.include_router(approvals.router)
app.include_router(settings.router)
app.include_router(corpus.router)
app.include_router(weather.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "database": db.backend_name()}
