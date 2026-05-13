from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.api.deps import get_db
from backend.api.schemas import (
    MeetingCard,
    MeetingDetail,
    MeetingDetailResponse,
    MeetingListResponse,
    Pagination,
    SupportingDocumentOut,
    AgendaItemDetail,
)
from backend.cache.client import cache_get, cache_set
from backend.config import settings
from backend.db.models import AgendaItem, Meeting, SupportingDocument

router = APIRouter(tags=["meetings"])


@router.get("/meetings", response_model=MeetingListResponse)
async def list_meetings(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    board: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"meetings:list:p={page}:l={limit}:b={board}"
    if cached := await cache_get(cache_key):
        return cached

    count_stmt = select(func.count()).select_from(Meeting).where(
        Meeting.processing_status == "completed"
    )
    stmt = (
        select(Meeting)
        .where(Meeting.processing_status == "completed")
        .order_by(Meeting.meeting_date.desc())
    )
    if board:
        count_stmt = count_stmt.where(Meeting.board_slug == board)
        stmt = stmt.where(Meeting.board_slug == board)

    total: int = (await db.execute(count_stmt)).scalar_one()
    rows = (await db.execute(stmt.offset((page - 1) * limit).limit(limit))).scalars().all()

    payload = MeetingListResponse(
        meetings=[MeetingCard.model_validate(m) for m in rows],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            has_next=(page * limit) < total,
        ),
    ).model_dump(mode="json")

    await cache_set(cache_key, payload)
    return payload


@router.get("/meetings/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: int,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"meetings:detail:{meeting_id}"
    if cached := await cache_get(cache_key):
        return cached

    stmt = (
        select(Meeting)
        .where(Meeting.id == meeting_id)
        .options(
            selectinload(Meeting.agenda_items),
            selectinload(Meeting.supporting_documents),
        )
    )
    meeting = (await db.execute(stmt)).scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    payload = MeetingDetailResponse(
        meeting=MeetingDetail(
            **MeetingCard.model_validate(meeting).model_dump(),
            source_url=meeting.source_url,
            source_pdf_url=meeting.source_pdf_url,
            next_meeting_notes=meeting.next_meeting_notes,
            updated_at=meeting.updated_at,
            agenda_items=[
                AgendaItemDetail.model_validate(i) for i in meeting.agenda_items
            ],
            supporting_documents=[
                SupportingDocumentOut.model_validate(d)
                for d in meeting.supporting_documents
            ],
        )
    ).model_dump(mode="json")

    await cache_set(cache_key, payload)
    return payload
