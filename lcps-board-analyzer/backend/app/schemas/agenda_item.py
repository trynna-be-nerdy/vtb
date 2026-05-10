"""Pydantic schemas for AgendaItem API responses."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgendaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    meeting_id: uuid.UUID
    item_order: int
    title: str
    summary: str
    decisions: list[str]
    action_items: list[str]
    key_figures: dict
    primary_category: str
    secondary_tags: list[str]
    urgency: str
    fiscal_impact: bool
    affects_schools: list[str]
    source_pdf_url: str | None
    page_range: str | None
    created_at: datetime
