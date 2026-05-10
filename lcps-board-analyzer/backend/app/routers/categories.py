"""GET /api/categories and GET /api/categories/{slug}"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AgendaItem
from app.schemas.agenda_item import AgendaItemOut
from app.schemas.category import CategoryOut, CategoryFeed
from app.services.cache import cache_get, cache_set

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["categories"])

CATEGORIES = [
    {"slug": "schools-education", "label": "Schools & Education", "description": "Curriculum, testing, calendars, special ed"},
    {"slug": "school-construction", "label": "School Construction", "description": "New buildings, renovations, CIP projects"},
    {"slug": "budget-finance", "label": "Budget & Finance", "description": "Budgets, audits, grants, debt, fiscal votes"},
    {"slug": "transportation", "label": "Transportation", "description": "Buses, VDOT, roads, sidewalks, traffic"},
    {"slug": "zoning-land-use", "label": "Zoning & Land Use", "description": "Rezonings, special exceptions, proffering"},
    {"slug": "public-safety", "label": "Public Safety", "description": "Safety protocols, SRO, emergency plans"},
    {"slug": "policy-governance", "label": "Policy & Governance", "description": "Board policy, ethics, appointments"},
    {"slug": "equity-inclusion", "label": "Equity & Inclusion", "description": "Title IX, language access, equity audits"},
    {"slug": "technology", "label": "Technology", "description": "EdTech, cybersecurity, FERPA, AI policy"},
    {"slug": "community-parks", "label": "Community & Parks", "description": "Facility use, afterschool, parks"},
    {"slug": "personnel", "label": "Personnel", "description": "Staff, compensation, labor agreements"},
    {"slug": "general", "label": "General", "description": "Catch-all for unclassified items"},
]
CATEGORY_MAP = {c["slug"]: c for c in CATEGORIES}


@router.get("", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    cache_key = "categories:list"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    # Count items per category
    counts_result = await db.execute(
        select(AgendaItem.primary_category, func.count().label("cnt"))
        .group_by(AgendaItem.primary_category)
    )
    counts = {row.primary_category: row.cnt for row in counts_result}

    response = [
        CategoryOut(
            slug=c["slug"],
            label=c["label"],
            description=c["description"],
            item_count=counts.get(c["slug"], 0),
        )
        for c in CATEGORIES
    ]
    await cache_set(cache_key, [r.model_dump() for r in response])
    return response


@router.get("/{slug}", response_model=CategoryFeed)
async def get_category_feed(
    slug: str,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    fiscal_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    if slug not in CATEGORY_MAP:
        raise HTTPException(status_code=404, detail=f"Category '{slug}' not found")

    cache_key = f"categories:{slug}:page={page}:size={page_size}:fiscal={fiscal_only}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    query = select(AgendaItem).where(AgendaItem.primary_category == slug)
    if fiscal_only:
        query = query.where(AgendaItem.fiscal_impact.is_(True))

    total_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    items_result = await db.execute(
        query.order_by(AgendaItem.created_at.desc()).offset(offset).limit(page_size)
    )
    items = items_result.scalars().all()

    cat_data = CATEGORY_MAP[slug]
    response = CategoryFeed(
        category=CategoryOut(slug=slug, label=cat_data["label"], description=cat_data["description"], item_count=total),
        items=[AgendaItemOut.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        has_next=(offset + page_size) < total,
    )
    await cache_set(cache_key, response.model_dump())
    return response
