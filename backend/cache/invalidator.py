"""
Cache invalidation helpers.

Called by the pipeline after each DB write so the API serves fresh data
immediately instead of waiting for TTL expiry.

Key patterns (must match what the route handlers write):
  meetings:list:p=*:l=*:b=*   — paginated meeting lists (all boards + per-board)
  meetings:detail:{id}         — single meeting detail
  categories:all               — category list with counts
  categories:feed:{slug}:*     — paginated category feeds
  health:status                — health / stats panel
  search:*                     — full-text search results (optional, low priority)
"""

import logging

from backend.cache.client import cache_delete, cache_delete_pattern

logger = logging.getLogger(__name__)


async def invalidate_meeting(meeting_id: int) -> None:
    """Clear the detail cache for one meeting and all paginated list caches."""
    await cache_delete(f"meetings:detail:{meeting_id}")
    await cache_delete_pattern("meetings:list:*")
    await cache_delete("health:status")
    logger.debug("Cache invalidated for meeting %s", meeting_id)


async def invalidate_category(slug: str) -> None:
    """Clear category feed pages and the global category count list."""
    await cache_delete_pattern(f"categories:feed:{slug}:*")
    await cache_delete("categories:all")
    logger.debug("Cache invalidated for category %s", slug)


async def invalidate_all_lists() -> None:
    """Broad invalidation after a full pipeline run — clears all list/feed caches."""
    await cache_delete_pattern("meetings:list:*")
    await cache_delete_pattern("categories:*")
    await cache_delete("health:status")
    logger.info("Full list cache invalidated after pipeline run")


async def invalidate_search() -> None:
    """Clear all search result caches (call when new items change search rankings)."""
    await cache_delete_pattern("search:*")
    logger.debug("Search cache invalidated")
