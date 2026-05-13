from datetime import datetime, date
from typing import Optional

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Index,
    Integer, String, Text, func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TSVECTOR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    scraper_type: Mapped[str] = mapped_column(String(50), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SeenDocument(Base):
    __tablename__ = "seen_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    # pending | processing | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="pending")
    source_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sources.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("ix_seen_documents_url", "url"),)


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    # lcps | supervisors | planning | advisory
    board_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(1000))
    source_pdf_url: Mapped[Optional[str]] = mapped_column(String(1000))

    # Gemma 4 Prompt 3 fields
    meeting_overview: Mapped[Optional[str]] = mapped_column(Text)
    top_decisions: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    fiscal_total: Mapped[Optional[str]] = mapped_column(String(100))
    next_meeting_notes: Mapped[Optional[str]] = mapped_column(Text)

    total_items: Mapped[int] = mapped_column(Integer, default=0)
    fiscal_items: Mapped[int] = mapped_column(Integer, default=0)
    # pending | processing | completed | failed
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    agenda_items: Mapped[list["AgendaItem"]] = relationship(
        back_populates="meeting", lazy="select"
    )
    supporting_documents: Mapped[list["SupportingDocument"]] = relationship(
        back_populates="meeting", lazy="select"
    )

    __table_args__ = (
        Index("ix_meetings_board_date", "board_slug", "meeting_date"),
        Index("ix_meetings_date", "meeting_date"),
        Index("ix_meetings_status", "processing_status"),
    )


class AgendaItem(Base):
    __tablename__ = "agenda_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )

    # Gemma 4 Prompt 1 fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    decisions: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    action_items: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    key_figures: Mapped[Optional[dict]] = mapped_column(JSONB)

    # Gemma 4 Prompt 2 fields
    primary_category: Mapped[str] = mapped_column(String(50), nullable=False)
    secondary_tags: Mapped[Optional[list]] = mapped_column(ARRAY(Text))
    urgency: Mapped[str] = mapped_column(String(20), default="routine")
    fiscal_impact: Mapped[bool] = mapped_column(Boolean, default=False)
    affects_schools: Mapped[Optional[list]] = mapped_column(ARRAY(Text))

    source_pdf_url: Mapped[Optional[str]] = mapped_column(String(1000))
    page_range: Mapped[Optional[str]] = mapped_column(String(50))
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="agenda_items")

    __table_args__ = (
        Index("ix_agenda_items_meeting_id", "meeting_id"),
        Index("ix_agenda_items_category", "primary_category"),
        Index("ix_agenda_items_urgency", "urgency"),
        Index("ix_agenda_items_fiscal", "fiscal_impact"),
        # GIN index for fast full-text search — populated by DB trigger
        Index(
            "ix_agenda_items_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
    )


class SupportingDocument(Base):
    __tablename__ = "supporting_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    meeting_id: Mapped[int] = mapped_column(
        ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(String(500))
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    doc_type: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    meeting: Mapped["Meeting"] = relationship(back_populates="supporting_documents")


class PipelineRun(Base):
    __tablename__ = "pipeline_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    # running | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="running")
    documents_found: Mapped[int] = mapped_column(Integer, default=0)
    documents_processed: Mapped[int] = mapped_column(Integer, default=0)
    items_created: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
