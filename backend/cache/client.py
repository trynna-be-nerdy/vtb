"""
Redis connection pool and cache-aside helpers.

A single ConnectionPool is shared across all coroutines in one worker process.
Every GET endpoint calls cache_get first; on a miss it queries Postgres,
then calls cache_set so subsequent requests are served from Redis.
"""

import json
from typing import Any

import redis.asyncio as aioredis

from backend.config import settings

_pool: aioredis.ConnectionPool | None = None

PUBSUB_CHANNEL = "vtb:updates"


def _get_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
    return _pool


def get_redis() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=_get_pool())


async def close_pool() -> None:
    global _pool
    if _pool:
        await _pool.aclose()
        _pool = None


# ── Cache helpers ────────────────────────────────────────────────────────────

async def cache_get(key: str) -> Any | None:
    r = get_redis()
    val = await r.get(key)
    return json.loads(val) if val is not None else None


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    r = get_redis()
    await r.set(
        key,
        json.dumps(value, default=str),
        ex=ttl if ttl is not None else settings.cache_ttl_seconds,
    )


async def cache_delete(key: str) -> None:
    r = get_redis()
    await r.delete(key)


async def cache_delete_pattern(pattern: str) -> None:
    """Invalidate all keys matching a glob pattern (e.g. 'meetings:*')."""
    r = get_redis()
    keys = await r.keys(pattern)
    if keys:
        await r.delete(*keys)


async def publish_update(payload: dict) -> None:
    """Broadcast a pipeline update event to all connected WebSocket clients."""
    r = get_redis()
    await r.publish(PUBSUB_CHANNEL, json.dumps(payload, default=str))
