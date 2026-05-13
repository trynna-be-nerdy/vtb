"""
FastAPI application entry point.

Scalability checklist for 100K–1M users:
  ✅ Async everywhere — never blocks the event loop
  ✅ Redis cache-aside on every GET endpoint (15-min TTL)
  ✅ Async PostgreSQL connection pool (pool_pre_ping, pool_recycle)
  ✅ GZip compression on responses > 1 KB
  ✅ CORS locked to known origins
  ✅ Per-IP rate limiting via slowapi
  ✅ WebSocket via Redis Pub/Sub — safe for multi-worker deployments
  ✅ Lifespan hooks close DB engine and Redis pool on shutdown
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from backend.api.routes import (
    categories,
    health,
    meetings,
    pipeline,
    search,
    websocket,
)
from backend.cache.client import close_pool
from backend.config import settings
from backend.db.database import engine

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[settings.rate_limit_default],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: nothing to do — pools initialise lazily on first request.
    yield
    # Shutdown: gracefully drain connections.
    await engine.dispose()
    await close_pool()


app = FastAPI(
    title="View the Board API",
    description="Plain-English summaries of Loudoun County government meetings, powered by Gemma 4.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ── Middleware (order matters — outermost applied last) ───────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(health.router,      prefix="/api")
app.include_router(meetings.router,    prefix="/api")
app.include_router(categories.router,  prefix="/api")
app.include_router(search.router,      prefix="/api")
app.include_router(pipeline.router,    prefix="/api")
app.include_router(websocket.router)
