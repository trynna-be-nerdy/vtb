"""Meeting — one row per board meeting."""
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    seen_document_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("seen_documents.id"), nullable=True
    )

    # Meeting metadata
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    source_pdf_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Gemma 4 — Prompt 3 output
    meeting_overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    top_decisions: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    fiscal_total: Mapped[str | None] = mapped_column(String(100), nullable=True)
    next_meeting_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Counts (denormalized for quick card display)
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    fiscal_items: Mapped[int] = mapped_column(Integer, default=0)

    # Processing state
    processing_status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source = relationship("Source", back_populates="meetings")
    seen_document = relationship("SeenDocument", back_populates="meeting")
    agenda_items = relationship("AgendaItem", back_populates="meeting", lazy="select", order_by="AgendaItem.item_order")
    supporting_documents = relationship("SupportingDocument", back_populates="meeting", lazy="select")
