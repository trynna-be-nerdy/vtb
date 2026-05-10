"""SeenDocument — deduplication table (URL + SHA-256 hash + status)."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SeenDocument(Base):
    __tablename__ = "seen_documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    sha256_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    # pending | processing | completed | failed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    source = relationship("Source", back_populates="seen_documents")
    meeting = relationship("Meeting", back_populates="seen_document", uselist=False)
