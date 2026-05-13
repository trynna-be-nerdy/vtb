"""
Real-time WebSocket endpoint backed by Redis Pub/Sub.

Each FastAPI worker process maintains its own subscriber. When the pipeline
publishes an update to the Redis channel, every connected client across all
worker instances receives it — supporting horizontal scaling.
"""

import asyncio

import redis.asyncio as aioredis
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.cache.client import PUBSUB_CHANNEL, get_redis

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    await websocket.accept()

    r: aioredis.Redis = get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(PUBSUB_CHANNEL)

    async def forward_to_client():
        async for message in pubsub.listen():
            if message["type"] == "message":
                await websocket.send_text(message["data"])

    forward_task = asyncio.create_task(forward_to_client())

    try:
        # Keep alive — detect client disconnect via receive
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        forward_task.cancel()
    finally:
        await pubsub.unsubscribe(PUBSUB_CHANNEL)
        await pubsub.aclose()
        await r.aclose()
