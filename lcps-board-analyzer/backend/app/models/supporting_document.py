"""SupportingDocument — attachments linked to a meeting (staff reports, presentations, etc.)."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SupportingDocument(Base):
    __tablename__ = "supporting_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    meeting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("meetings.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "staff_report" | "presentation" | "budget" | "other"
    url: Mapped[str] = mapped_column(Text, nullable=False)
    # Gemma 4 summary if processed (P2 feature)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    meeting = relationship("Meeting", back_populates="supporting_documents")
