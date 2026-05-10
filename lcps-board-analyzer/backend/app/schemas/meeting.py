"""Pydantic schemas for Meeting API responses."""
import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from .agenda_item import AgendaItemOut


class SupportingDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    document_type: str
    url: str
    summary: str | None


class MeetingCard(BaseModel):
    """Lightweight meeting representation for cards/lists."""
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    meeting_date: date
    source_url: str
    meeting_overview: str | None
    top_decisions: list[str] | None
    fiscal_total: str | None
    total_items: int
    fiscal_items: int
    processing_status: str
    created_at: datetime


class MeetingDetail(MeetingCard):
    """Full meeting detail with all agenda items and supporting docs."""
    next_meeting_notes: str | None
    agenda_items: list[AgendaItemOut] = []
    supporting_documents: list[SupportingDocumentOut] = []


class PaginatedMeetings(BaseModel):
    items: list[MeetingCard]
    total: int
    page: int
    page_size: int
    has_next: bool
