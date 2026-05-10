"""GET /api/search?q= — PostgreSQL full-text search."""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AgendaItem
from app.schemas.agenda_item import AgendaItemOut
from app.schemas.category import SearchResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("", response_model=SearchResult)
async def search(
    q: Annotated[str, Query(min_length=2, max_length=200)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=50)] = 20,
    db: AsyncSession = Depends(get_db),
):
    """Full-text search across title, summary, and decisions using PostgreSQL tsvector."""
    tsquery = func.plainto_tsquery("english", q)

    base_query = (
        select(AgendaItem)
        .where(AgendaItem.search_vector.op("@@")(tsquery))
        .order_by(func.ts_rank(AgendaItem.search_vector, tsquery).desc())
    )

    total_result = await db.execute(
        select(func.count()).select_from(base_query.subquery())
    )
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    items_result = await db.execute(base_query.offset(offset).limit(page_size))
    items = items_result.scalars().all()

    return SearchResult(
        items=[AgendaItemOut.model_validate(i) for i in items],
        total=total,
        query=q,
    )
