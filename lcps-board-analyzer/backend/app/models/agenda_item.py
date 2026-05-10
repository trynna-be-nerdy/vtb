"""AgendaItem — the core content unit (one per agenda item, output of Gemma 4 Prompts 1 & 2)."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AgendaItem(Base):
    __tablename__ = "agenda_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True)
    item_order: Mapped[int] = mapped_column(Integer, default=0)

    # --- Gemma 4 Prompt 1 output ---
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    decisions: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    action_items: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False, default=list)
    # key_figures: { "amounts": [...], "vote_tallies": [...], "dates": [...], "schools": [...] }
    key_figures: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # --- Gemma 4 Prompt 2 output ---
    # One of 12 category slugs
    primary_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    secondary_tags: Mapped[list[str]] = mapped_column(ARRAY(String(50)), nullable=False, default=list)
    # "routine" | "notable" | "significant"
    urgency: Mapped[str] = mapped_column(String(20), nullable=False, default="routine")
    fiscal_impact: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    affects_schools: Mapped[list[str]] = mapped_column(ARRAY(String(200)), nullable=False, default=list)

    # Source traceability
    source_pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_range: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "pp. 12–15"
    raw_chunk: Mapped[str | None] = mapped_column(Text, nullable=True)  # original PDF text (debug)

    # Full-text search vector — auto-updated by PostgreSQL trigger
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    meeting = relationship("Meeting", back_populates="agenda_items")

    __table_args__ = (
        Index("ix_agenda_items_search_vector", "search_vector", postgresql_using="gin"),
        Index("ix_agenda_items_primary_category", "primary_category"),
        Index("ix_agenda_items_urgency", "urgency"),
        Index("ix_agenda_items_fiscal_impact", "fiscal_impact"),
    )
