"""GET /api/meetings and GET /api/meetings/{id}"""
import uuid
import json
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Meeting, AgendaItem
from app.schemas.meeting import MeetingCard, MeetingDetail, PaginatedMeetings
from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=PaginatedMeetings)
async def list_meetings(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"meetings:list:page={page}:size={page_size}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    offset = (page - 1) * page_size
    total_result = await db.execute(
        select(func.count()).where(Meeting.processing_status == "completed")
    )
    total = total_result.scalar_one()

    result = await db.execute(
        select(Meeting)
        .where(Meeting.processing_status == "completed")
        .order_by(Meeting.meeting_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    meetings = result.scalars().all()

    response = PaginatedMeetings(
        items=[MeetingCard.model_validate(m) for m in meetings],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )
    await cache_set(cache_key, response.model_dump())
    return response


@router.get("/{meeting_id}", response_model=MeetingDetail)
async def get_meeting(meeting_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cache_key = f"meetings:detail:{meeting_id}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(Meeting)
        .options(
            selectinload(Meeting.agenda_items),
            selectinload(Meeting.supporting_documents),
        )
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    response = MeetingDetail.model_validate(meeting)
    await cache_set(cache_key, response.model_dump())
    return response
