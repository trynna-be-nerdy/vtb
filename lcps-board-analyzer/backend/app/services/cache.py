"""Redis cache service — get/set JSON with TTL, invalidate on new content."""
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def cache_get(key: str) -> Any | None:
    try:
        redis = await get_redis()
        value = await redis.get(key)
        if value:
            return json.loads(value)
    except Exception as exc:
        logger.warning("Cache GET failed for key=%s: %s", key, exc)
    return None


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    try:
        redis = await get_redis()
        ttl = ttl or settings.redis_cache_ttl
        await redis.setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.warning("Cache SET failed for key=%s: %s", key, exc)


async def cache_invalidate(pattern: str) -> int:
    """Delete all keys matching a glob pattern. Returns number of deleted keys."""
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            return await redis.delete(*keys)
    except Exception as exc:
        logger.warning("Cache INVALIDATE failed for pattern=%s: %s", pattern, exc)
    return 0


async def cache_publish(channel: str, message: dict) -> None:
    """Publish a message to a Redis Pub/Sub channel (for WebSocket broadcast)."""
    try:
        redis = await get_redis()
        await redis.publish(channel, json.dumps(message, default=str))
    except Exception as exc:
        logger.warning("Cache PUBLISH failed for channel=%s: %s", channel, exc)
