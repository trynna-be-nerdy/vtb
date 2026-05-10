"""WebSocket connection manager + Redis Pub/Sub broadcast."""
import asyncio
import json
import logging

from fastapi import WebSocket

from app.services.cache import get_redis

logger = logging.getLogger(__name__)

PUBSUB_CHANNEL = "lcps:new_content"


class ConnectionManager:
    def __init__(self) -> None:
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.active.append(ws)
        logger.info("WebSocket connected. Total connections: %d", len(self.active))

    def disconnect(self, ws: WebSocket) -> None:
        self.active = [c for c in self.active if c != ws]
        logger.info("WebSocket disconnected. Total connections: %d", len(self.active))

    async def broadcast(self, message: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)


manager = ConnectionManager()


async def redis_subscriber() -> None:
    """Long-running coroutine: subscribes to Redis and forwards messages to all WebSocket clients."""
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.subscribe(PUBSUB_CHANNEL)
    logger.info("Redis subscriber started on channel: %s", PUBSUB_CHANNEL)
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                data = json.loads(message["data"])
                await manager.broadcast(data)
            except Exception as exc:
                logger.warning("Failed to broadcast WebSocket message: %s", exc)
