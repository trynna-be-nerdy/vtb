from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


# ── Shared ───────────────────────────────────────────────────────────────────

class Pagination(BaseModel):
    page: int
    limit: int
    total: int
    has_next: bool


# ── Agenda items ─────────────────────────────────────────────────────────────

class AgendaItemCard(BaseModel):
    id: int
    meeting_id: int
    title: str
    summary: str
    primary_category: str
    secondary_tags: Optional[list[str]]
    urgency: str
    fiscal_impact: bool
    affects_schools: Optional[list[str]]
    source_pdf_url: Optional[str]
    page_range: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AgendaItemDetail(AgendaItemCard):
    decisions: Optional[list[str]]
    action_items: Optional[list[str]]
    key_figures: Optional[dict]


# ── Meetings ─────────────────────────────────────────────────────────────────

class MeetingCard(BaseModel):
    id: int
    title: str
    board_slug: str
    meeting_date: date
    meeting_overview: Optional[str]
    top_decisions: Optional[list[str]]
    fiscal_total: Optional[str]
    total_items: int
    fiscal_items: int
    processing_status: str

    model_config = {"from_attributes": True}


class MeetingDetail(MeetingCard):
    source_url: Optional[str]
    source_pdf_url: Optional[str]
    next_meeting_notes: Optional[str]
    agenda_items: list[AgendaItemDetail]
    supporting_documents: list["SupportingDocumentOut"]
    updated_at: datetime


class SupportingDocumentOut(BaseModel):
    id: int
    title: Optional[str]
    url: str
    doc_type: Optional[str]

    model_config = {"from_attributes": True}


MeetingDetail.model_rebuild()


class MeetingListResponse(BaseModel):
    meetings: list[MeetingCard]
    pagination: Pagination


class MeetingDetailResponse(BaseModel):
    meeting: MeetingDetail


# ── Categories ───────────────────────────────────────────────────────────────

CATEGORY_LABELS: dict[str, str] = {
    "schools-education": "Schools & Education",
    "school-construction": "School Construction",
    "budget-finance": "Budget & Finance",
    "transportation": "Transportation",
    "zoning-land-use": "Zoning & Land Use",
    "public-safety": "Public Safety",
    "policy-governance": "Policy & Governance",
    "equity-inclusion": "Equity & Inclusion",
    "technology": "Technology",
    "community-parks": "Community & Parks",
    "personnel": "Personnel",
    "general": "General",
}


class CategoryInfo(BaseModel):
    slug: str
    label: str
    item_count: int


class CategoryListResponse(BaseModel):
    categories: list[CategoryInfo]


class CategoryFeedResponse(BaseModel):
    slug: str
    label: str
    items: list[AgendaItemCard]
    pagination: Pagination


# ── Search ───────────────────────────────────────────────────────────────────

class SearchResult(AgendaItemCard):
    meeting_title: str
    meeting_date: date
    board_slug: str
    rank: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    pagination: Pagination


# ── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    last_pipeline_run: Optional[datetime]
    last_pipeline_status: Optional[str]
    items_this_month: int
    queue_depth: int


# ── Pipeline ─────────────────────────────────────────────────────────────────

class PipelineTriggerResponse(BaseModel):
    triggered: bool
    message: str
