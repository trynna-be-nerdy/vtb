from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.api.schemas import AgendaItemCard, Pagination, SearchResponse, SearchResult
from backend.cache.client import cache_get, cache_set
from backend.config import settings
from backend.db.models import AgendaItem, Meeting

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=2, max_length=200),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"search:{q}:p={page}:l={limit}"
    if cached := await cache_get(cache_key):
        return cached

    tsquery = func.plainto_tsquery("english", q)

    count_stmt = (
        select(func.count())
        .select_from(AgendaItem)
        .where(AgendaItem.search_vector.op("@@")(tsquery))
    )
    total: int = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(
            AgendaItem,
            Meeting.title.label("meeting_title"),
            Meeting.meeting_date.label("meeting_date"),
            Meeting.board_slug.label("board_slug"),
            func.ts_rank(AgendaItem.search_vector, tsquery).label("rank"),
        )
        .join(Meeting, AgendaItem.meeting_id == Meeting.id)
        .where(AgendaItem.search_vector.op("@@")(tsquery))
        .order_by(text("rank DESC"))
        .offset((page - 1) * limit)
        .limit(limit)
    )

    rows = (await db.execute(stmt)).all()

    results = [
        SearchResult(
            **AgendaItemCard.model_validate(row.AgendaItem).model_dump(),
            meeting_title=row.meeting_title,
            meeting_date=row.meeting_date,
            board_slug=row.board_slug,
            rank=float(row.rank),
        )
        for row in rows
    ]

    payload = SearchResponse(
        query=q,
        results=results,
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            has_next=(page * limit) < total,
        ),
    ).model_dump(mode="json")

    await cache_set(cache_key, payload, ttl=settings.search_cache_ttl_seconds)
    return payload
