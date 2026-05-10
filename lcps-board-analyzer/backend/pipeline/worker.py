"""Pipeline worker — the autonomous engine that runs every 6 hours.

Run this as a SEPARATE process from the FastAPI server:
    python -m pipeline.worker

Architecture:
  Scraper → Deduplicator → Downloader → Extractor → Chunker
  → Gemma 4 Pass 1 → Gemma 4 Pass 2 → Validator → DB write
  → Redis invalidate → WebSocket broadcast
"""
import asyncio
import logging
import sys
import uuid
from datetime import datetime, date

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

# Use synchronous engine in the pipeline worker (separate process)
from app.config import get_settings
from app.models import Meeting, SeenDocument, Source, PipelineRun, AgendaItem
from pipeline.scraper import discover_all_documents, DiscoveredDocument
from pipeline.extractor import download_pdf, extract_text_from_bytes
from pipeline.chunker import split_into_chunks
from pipeline.gemma import analyze_chunk, classify_item, generate_meeting_overview, GemmaError
from pipeline.validator import validate_item, ValidationError
from pipeline.publisher import write_agenda_item, update_meeting_overview, invalidate_and_broadcast

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()

# Synchronous DB URL (replace asyncpg with psycopg2)
SYNC_DB_URL = settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
engine = create_engine(SYNC_DB_URL, pool_size=5)


def run_pipeline() -> None:
    """Full pipeline run — called by APScheduler every 6 hours."""
    logger.info("=== Pipeline run starting ===")
    with Session(engine) as db:
        run = PipelineRun(started_at=datetime.utcnow())
        db.add(run)
        db.commit()

        try:
            _execute_pipeline(db, run)
            run.status = "completed"
            run.finished_at = datetime.utcnow()
            db.commit()
            logger.info(
                "=== Pipeline run completed: %d new docs, %d items processed, %d failed ===",
                run.documents_new, run.items_processed, run.items_failed,
            )
        except Exception as exc:
            logger.exception("Pipeline run failed: %s", exc)
            run.status = "failed"
            run.error_message = str(exc)
            run.finished_at = datetime.utcnow()
            db.commit()


def _execute_pipeline(db: Session, run: PipelineRun) -> None:
    # 1. Discover documents
    discovered = discover_all_documents()
    run.documents_found = len(discovered)
    db.commit()

    for doc in discovered:
        _process_document(db, run, doc)


def _process_document(db: Session, run: PipelineRun, doc: DiscoveredDocument) -> None:
    # 2. Deduplicate
    existing = db.execute(select(SeenDocument).where(SeenDocument.url == doc.url)).scalar_one_or_none()
    if existing and existing.status == "completed":
        logger.debug("Skipping already-processed document: %s", doc.url)
        return

    try:
        # 3. Download + hash
        pdf_bytes, sha256 = download_pdf(doc.url)

        if existing:
            if existing.sha256_hash == sha256:
                logger.debug("Document unchanged (same hash): %s", doc.url)
                return
            existing.sha256_hash = sha256
            existing.status = "processing"
            seen_doc = existing
        else:
            # Get or create source
            source = db.execute(
                select(Source).where(Source.source_type == doc.source_type)
            ).scalar_one_or_none()
            if not source:
                logger.warning("No source configured for type '%s', skipping", doc.source_type)
                return

            seen_doc = SeenDocument(
                source_id=source.id,
                url=doc.url,
                sha256_hash=sha256,
                status="processing",
            )
            db.add(seen_doc)
            db.flush()
            run.documents_new += 1

        # 4. Create or get meeting row
        meeting = Meeting(
            source_id=seen_doc.source_id,
            seen_document_id=seen_doc.id,
            title=doc.title,
            meeting_date=date.fromisoformat(doc.meeting_date) if doc.meeting_date else date.today(),
            source_url=doc.url,
            source_pdf_url=doc.url,
            processing_status="processing",
        )
        db.add(meeting)
        db.flush()
        db.commit()

        # 5. Extract + chunk
        pages = extract_text_from_bytes(pdf_bytes)
        chunks = split_into_chunks(pages)

        # 6 & 7. Gemma 4 Pass 1 + 2 per chunk
        item_order = 0
        summaries_for_overview: list[str] = []

        for chunk in chunks:
            try:
                prompt1 = analyze_chunk(chunk)
                prompt2 = classify_item(prompt1["summary"])
                validate_item(prompt1, prompt2)
                write_agenda_item(db, meeting.id, item_order, prompt1, prompt2, doc.url, chunk)
                summaries_for_overview.append(prompt1["summary"])
                item_order += 1
                run.items_processed += 1
                db.commit()

                # Async publish — fire and forget
                asyncio.run(invalidate_and_broadcast(prompt2["primary_category"], meeting.id))

            except (GemmaError, ValidationError) as exc:
                logger.warning("Item failed validation/Gemma: %s", exc)
                run.items_failed += 1

        # 8. Prompt 3 — meeting overview
        if summaries_for_overview:
            try:
                overview = generate_meeting_overview(summaries_for_overview)
                update_meeting_overview(db, meeting, overview)
            except GemmaError as exc:
                logger.warning("Meeting overview generation failed: %s", exc)
                meeting.processing_status = "completed"

        meeting.total_items = item_order
        meeting.fiscal_items = db.query(AgendaItem).filter(
            AgendaItem.meeting_id == meeting.id, AgendaItem.fiscal_impact.is_(True)
        ).count()
        seen_doc.status = "completed"
        seen_doc.processed_at = datetime.utcnow()
        db.commit()

    except Exception as exc:
        logger.error("Failed to process document %s: %s", doc.url, exc)
        run.items_failed += 1
        if existing:
            existing.status = "failed"
            existing.error_message = str(exc)
            db.commit()


def main() -> None:
    logger.info("Starting pipeline worker (interval: every %d hours)", settings.pipeline_interval_hours)
    # Run once immediately on startup
    run_pipeline()

    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(
        run_pipeline,
        "interval",
        hours=settings.pipeline_interval_hours,
        id="pipeline_main",
    )
    scheduler.start()


if __name__ == "__main__":
    main()
