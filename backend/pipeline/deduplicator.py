"""
Deduplication logic for the VtB ingestion pipeline.

Checks incoming DocumentInfo objects against the seen_documents table and
skips any URL whose content hash already exists with status 'completed'.
"""

import hashlib
import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import SeenDocument
from backend.pipeline.scrapers.base import DocumentInfo

logger = logging.getLogger(__name__)


async def is_already_processed(session: AsyncSession, url: str, content_hash: str) -> bool:
    """Return True if *url* is in seen_documents with status='completed' AND the same hash."""
    result = await session.execute(
        select(SeenDocument).where(SeenDocument.url == url)
    )
    record: Optional[SeenDocument] = result.scalar_one_or_none()

    if record is None:
        return False
    if record.status == "completed" and record.sha256 == content_hash:
        logger.debug("Skipping already-processed URL: %s", url)
        return True
    return False


async def upsert_seen_document(
    session: AsyncSession,
    url: str,
    content: bytes,
    *,
    status: str = "pending",
    source_id: Optional[int] = None,
) -> SeenDocument:
    """Insert or update a SeenDocument record for *url*.

    Returns the persisted record. Caller is responsible for committing the session.
    """
    content_hash = hashlib.sha256(content).hexdigest()

    result = await session.execute(
        select(SeenDocument).where(SeenDocument.url == url)
    )
    record: Optional[SeenDocument] = result.scalar_one_or_none()

    if record is None:
        record = SeenDocument(
            url=url,
            sha256=content_hash,
            status=status,
            source_id=source_id,
        )
        session.add(record)
    else:
        record.sha256 = content_hash
        record.status = status
        if source_id is not None:
            record.source_id = source_id

    return record


async def filter_new_documents(
    session: AsyncSession,
    documents: list[DocumentInfo],
) -> list[DocumentInfo]:
    """Filter *documents* to only those not yet successfully processed.

    Uses a single batched query to check all URLs efficiently.
    """
    if not documents:
        return []

    urls = [doc.pdf_url for doc in documents]
    result = await session.execute(
        select(SeenDocument.url, SeenDocument.sha256, SeenDocument.status).where(
            SeenDocument.url.in_(urls)
        )
    )
    existing: dict[str, tuple[str, str]] = {
        row.url: (row.sha256, row.status) for row in result
    }

    new_docs: list[DocumentInfo] = []
    for doc in documents:
        record = existing.get(doc.pdf_url)
        if record is None:
            new_docs.append(doc)
            continue
        sha256, status = record
        if status != "completed":
            new_docs.append(doc)
        else:
            logger.debug("Deduplicator skipping completed URL: %s", doc.pdf_url)

    logger.info(
        "Deduplicator: %d total, %d new, %d skipped",
        len(documents),
        len(new_docs),
        len(documents) - len(new_docs),
    )
    return new_docs
