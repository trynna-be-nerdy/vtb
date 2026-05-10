"""FastAPI application entry point."""
import asyncio
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    meetings_router,
    categories_router,
    search_router,
    health_router,
    pipeline_router,
)
from app.services.websocket import manager, redis_subscriber

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Civic AI that reads LCPS board meetings so residents don't have to.",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(meetings_router)
app.include_router(categories_router)
app.include_router(search_router)
app.include_router(health_router)
app.include_router(pipeline_router)


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting LCPS Board Meeting Analyzer API v%s", settings.app_version)
    # Start Redis subscriber for WebSocket broadcast
    asyncio.create_task(redis_subscriber())


@app.websocket("/ws/updates")
async def websocket_updates(ws: WebSocket) -> None:
    """Real-time push when new agenda items are processed."""
    await manager.connect(ws)
    try:
        while True:
            # Keep connection alive — client sends pings
            await ws.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(ws)


@app.get("/")
async def root():
    return {"name": settings.app_name, "version": settings.app_version, "docs": "/docs"}
