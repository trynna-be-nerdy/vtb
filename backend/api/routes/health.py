from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.api.schemas import HealthResponse
from backend.cache.client import cache_get, cache_set
from backend.config import settings
from backend.db.models import AgendaItem, PipelineRun, SeenDocument

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)):
    cache_key = "health:status"
    if cached := await cache_get(cache_key):
        return cached

    # Last pipeline run
    last_run = (
        await db.execute(
            select(PipelineRun).order_by(PipelineRun.started_at.desc()).limit(1)
        )
    ).scalar_one_or_none()

    # Items created this calendar month
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    items_this_month: int = (
        await db.execute(
            select(func.count())
            .select_from(AgendaItem)
            .where(AgendaItem.created_at >= month_start)
        )
    ).scalar_one()

    # Pending docs = queue depth
    queue_depth: int = (
        await db.execute(
            select(func.count())
            .select_from(SeenDocument)
            .where(SeenDocument.status.in_(["pending", "processing"]))
        )
    ).scalar_one()

    payload = HealthResponse(
        status="ok",
        last_pipeline_run=last_run.started_at if last_run else None,
        last_pipeline_status=last_run.status if last_run else None,
        items_this_month=items_this_month,
        queue_depth=queue_depth,
    ).model_dump(mode="json")

    await cache_set(cache_key, payload, ttl=settings.health_cache_ttl_seconds)
    return payload
