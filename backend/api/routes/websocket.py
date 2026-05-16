"""
Real-time WebSocket endpoint backed by Redis Pub/Sub.

Each FastAPI worker process maintains its own subscriber. When the pipeline
publishes an update to the Redis channel, every connected client across all
worker instances receives it — supporting horizontal scaling.

Heartbeat: the server sends a ping frame every PING_INTERVAL seconds and
expects a pong within PONG_TIMEOUT seconds. Stale connections are closed
instead of silently accumulating.
"""

import asyncio
import logging

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.cache.client import PUBSUB_CHANNEL, get_redis

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

PING_INTERVAL = 30   # seconds between server pings
PONG_TIMEOUT  = 10   # seconds to wait for client pong before closing


@router.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    await websocket.accept()

    r: aioredis.Redis = get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(PUBSUB_CHANNEL)

    pong_event = asyncio.Event()

    async def forward_to_client():
        """Forward Redis pub/sub messages to the WebSocket client."""
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])

    async def heartbeat():
        """Send periodic pings; close the connection if no pong arrives."""
        while True:
            await asyncio.sleep(PING_INTERVAL)
            pong_event.clear()
            await websocket.send_text('{"type":"ping"}')
            try:
                await asyncio.wait_for(pong_event.wait(), timeout=PONG_TIMEOUT)
            except asyncio.TimeoutError:
                logger.warning("WebSocket client timed out — closing stale connection")
                await websocket.close(code=1001)
                return

    forward_task   = asyncio.create_task(forward_to_client())
    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        # Handle incoming client messages (pong replies, etc.)
        while True:
            data = await websocket.receive_text()
            if data == '{"type":"pong"}' or data == "pong":
                pong_event.set()
    except WebSocketDisconnect:
        pass
    finally:
        forward_task.cancel()
        heartbeat_task.cancel()
        await pubsub.unsubscribe(PUBSUB_CHANNEL)
        await pubsub.aclose()
        await r.aclose()
