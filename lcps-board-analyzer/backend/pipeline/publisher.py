"""DB write + Redis cache invalidation + WebSocket broadcast.

After Gemma 4 analysis and validation pass, publisher commits the item
to PostgreSQL, invalidates affected Redis keys, and broadcasts a
WebSocket notification to all connected frontend clients.
"""
import logging
import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import AgendaItem, Meeting
from app.services.cache import cache_invalidate, cache_publish

logger = logging.getLogger(__name__)

WS_CHANNEL = "lcps:new_content"


def write_agenda_item(
    db: Session,
    meeting_id: uuid.UUID,
    item_order: int,
    prompt1: dict,
    prompt2: dict,
    source_pdf_url: str | None,
    raw_chunk: str,
) -> AgendaItem:
    """Write a validated agenda item to the database (synchronous session)."""
    item = AgendaItem(
        meeting_id=meeting_id,
        item_order=item_order,
        title=prompt1["title"],
        summary=prompt1["summary"],
        decisions=prompt1.get("decisions", []),
        action_items=prompt1.get("action_items", []),
        key_figures=prompt1.get("key_figures", {}),
        primary_category=prompt2["primary_category"],
        secondary_tags=prompt2.get("secondary_tags", []),
        urgency=prompt2.get("urgency", "routine"),
        fiscal_impact=bool(prompt2.get("fiscal_impact", False)),
        affects_schools=prompt2.get("affects_schools", []),
        source_pdf_url=source_pdf_url,
        raw_chunk=raw_chunk,
    )
    db.add(item)
    db.flush()  # get ID without commit
    return item


def update_meeting_overview(db: Session, meeting: Meeting, overview_data: dict) -> None:
    """Apply Prompt 3 output to the meeting row."""
    meeting.meeting_overview = overview_data.get("meeting_overview")
    meeting.top_decisions = overview_data.get("top_decisions", [])
    meeting.fiscal_total = overview_data.get("fiscal_total")
    meeting.next_meeting_notes = overview_data.get("next_meeting_notes")
    meeting.processing_status = "completed"
    db.flush()


async def invalidate_and_broadcast(category_slug: str, meeting_id: uuid.UUID) -> None:
    """Invalidate Redis caches and push WebSocket notification."""
    # Invalidate affected cache keys
    await cache_invalidate("meetings:list:*")
    await cache_invalidate(f"meetings:detail:{meeting_id}")
    await cache_invalidate(f"categories:{category_slug}:*")
    await cache_invalidate("categories:list")

    # Broadcast to WebSocket clients
    await cache_publish(WS_CHANNEL, {
        "type": "new_item",
        "meeting_id": str(meeting_id),
        "category": category_slug,
        "timestamp": datetime.utcnow().isoformat(),
    })
    logger.info("Published new_item event for meeting=%s category=%s", meeting_id, category_slug)
