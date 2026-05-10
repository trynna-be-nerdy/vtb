"""GET /api/health — pipeline status and last run info."""
import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PipelineRun, AgendaItem, Meeting
from sqlalchemy import func

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    last_run_at: datetime | None
    last_run_status: str | None
    items_processed_last_run: int | None
    total_meetings: int
    total_agenda_items: int
    pipeline_queue_depth: int


@router.get("", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    # Latest pipeline run
    run_result = await db.execute(
        select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(1)
    )
    last_run = run_result.scalar_one_or_none()

    # Totals
    total_meetings = (await db.execute(select(func.count(Meeting.id)))).scalar_one()
    total_items = (await db.execute(select(func.count(AgendaItem.id)))).scalar_one()

    # Queue depth = meetings with processing_status = 'pending'
    queue_depth = (
        await db.execute(
            select(func.count(Meeting.id)).where(Meeting.processing_status == "pending")
        )
    ).scalar_one()

    return HealthResponse(
        status="ok",
        last_run_at=last_run.started_at if last_run else None,
        last_run_status=last_run.status if last_run else None,
        items_processed_last_run=last_run.items_processed if last_run else None,
        total_meetings=total_meetings,
        total_agenda_items=total_items,
        pipeline_queue_depth=queue_depth,
    )
