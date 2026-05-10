"""Pydantic schemas for category API responses."""
from pydantic import BaseModel

from .agenda_item import AgendaItemOut


class CategoryOut(BaseModel):
    slug: str
    label: str
    description: str
    item_count: int
    recent_activity_overview: str | None = None


class CategoryFeed(BaseModel):
    category: CategoryOut
    items: list[AgendaItemOut]
    total: int
    page: int
    page_size: int
    has_next: bool


class SearchResult(BaseModel):
    items: list[AgendaItemOut]
    total: int
    query: str
