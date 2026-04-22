from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import backtests as backtests_api
from app.api import bots as bots_api
from app.api import keys as keys_api
from app.api import orders as orders_api
from app.auth import routes as auth_routes
from app.config import get_settings
from app.db import Base, engine
from app.services.scheduler import shutdown_scheduler, start_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Auto-create tables on first boot for the SQLite default; real deployments
    # should run Alembic migrations instead.
    Base.metadata.create_all(bind=engine)
    if settings.scheduler_enabled:
        start_scheduler()
    try:
        yield
    finally:
        shutdown_scheduler()


app = FastAPI(
    title="Crypto Auto-Trader",
    version="0.1.0",
    description="Multi-strategy backtester and auto-trader for Binance / Coinbase / Kraken.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(keys_api.router)
app.include_router(backtests_api.router)
app.include_router(bots_api.router)
app.include_router(orders_api.router)


@app.get("/api/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
