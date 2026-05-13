from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.api.schemas import (
    AgendaItemCard,
    CATEGORY_LABELS,
    CategoryFeedResponse,
    CategoryInfo,
    CategoryListResponse,
    Pagination,
)
from backend.cache.client import cache_get, cache_set
from backend.db.models import AgendaItem

router = APIRouter(tags=["categories"])

_ALL_SLUGS = list(CATEGORY_LABELS.keys())


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(db: AsyncSession = Depends(get_db)):
    cache_key = "categories:all"
    if cached := await cache_get(cache_key):
        return cached

    rows = (
        await db.execute(
            select(AgendaItem.primary_category, func.count().label("cnt"))
            .group_by(AgendaItem.primary_category)
        )
    ).all()

    counts = {slug: 0 for slug in _ALL_SLUGS}
    for slug, cnt in rows:
        if slug in counts:
            counts[slug] = cnt

    payload = CategoryListResponse(
        categories=[
            CategoryInfo(
                slug=slug,
                label=CATEGORY_LABELS[slug],
                item_count=counts[slug],
            )
            for slug in _ALL_SLUGS
        ]
    ).model_dump(mode="json")

    await cache_set(cache_key, payload)
    return payload


@router.get("/categories/{slug}", response_model=CategoryFeedResponse)
async def get_category_feed(
    slug: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    if slug not in CATEGORY_LABELS:
        raise HTTPException(status_code=404, detail=f"Unknown category: {slug}")

    cache_key = f"categories:feed:{slug}:p={page}:l={limit}"
    if cached := await cache_get(cache_key):
        return cached

    base = select(AgendaItem).where(AgendaItem.primary_category == slug)
    total: int = (
        await db.execute(
            select(func.count()).select_from(AgendaItem).where(
                AgendaItem.primary_category == slug
            )
        )
    ).scalar_one()

    items = (
        await db.execute(
            base.order_by(AgendaItem.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
    ).scalars().all()

    payload = CategoryFeedResponse(
        slug=slug,
        label=CATEGORY_LABELS[slug],
        items=[AgendaItemCard.model_validate(i) for i in items],
        pagination=Pagination(
            page=page,
            limit=limit,
            total=total,
            has_next=(page * limit) < total,
        ),
    ).model_dump(mode="json")

    await cache_set(cache_key, payload)
    return payload
