"""Source — config for each monitored website."""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "lcps" | "loudoun_bos"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    scraper_class: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    seen_documents = relationship("SeenDocument", back_populates="source", lazy="select")
    meetings = relationship("Meeting", back_populates="source", lazy="select")
