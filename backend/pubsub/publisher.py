"""
Publisher helpers for broadcasting pipeline events to WebSocket clients.

Call publish_new_item() after each agenda item is successfully written to the
database. Redis failures are logged and swallowed so a pub/sub outage never
crashes the pipeline.
"""

import logging
from datetime import datetime, timezone

from backend.cache.client import publish_update
from backend.cache.invalidator import invalidate_meeting, invalidate_category

logger = logging.getLogger(__name__)


async def publish_new_item(
    *,
    meeting_id: int,
    item_id: int,
    title: str,
    category: str,
) -> None:
    """Invalidate relevant caches then broadcast a new-item event to all clients."""
    # 1. Bust caches so next API request returns fresh data
    try:
        await invalidate_meeting(meeting_id)
        await invalidate_category(category)
    except Exception:
        logger.exception(
            "Cache invalidation failed for meeting_id=%s item_id=%s — stale data may persist until TTL",
            meeting_id,
            item_id,
        )

    # 2. Broadcast real-time notification (swallow failures independently)
    payload = {
        "type": "new_item",
        "meeting_id": meeting_id,
        "item_id": item_id,
        "title": title,
        "category": category,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await publish_update(payload)
    except Exception:
        logger.exception(
            "Redis publish failed for item_id=%s — clients will not receive real-time update",
            item_id,
        )
