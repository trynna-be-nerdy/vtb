"""
Pipeline worker — runs on a schedule via APScheduler.

Full flow per discovered document:
  1. Download PDF from pdf_url
  2. Extract text with pdfplumber
  3. Chunk by agenda item
  4. Per chunk: Gemma rewrite (Prompt 1) + classify (Prompt 2)
  5. Write Meeting + AgendaItems to DB (atomic transaction)
  6. Gemma meeting overview (Prompt 3)
  7. Update Meeting.meeting_overview
  8. Bust Redis caches
  9. Publish Redis pub/sub notification

Start with:
    python -m backend.pipeline.worker
"""

import asyncio
import logging
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 3600  # every hour


async def run_scrape_cycle() -> None:
    logger.info("Scrape cycle started")
    try:
        from backend.pipeline.scrapers.loudoun_scraper import LoudounScraper
        from backend.pipeline.scrapers.lcps_scraper import LCPSScraper
        from backend.pipeline import process_pdf
        from backend.pipeline.downloader import DownloadError
        from backend.llm.ollama_client import rewrite_content, classify_content, generate_meeting_overview
        from backend.cache.invalidator import invalidate_all_lists, invalidate_search
        from backend.db.database import async_session
        from backend.db import models
        from sqlalchemy import select
        from datetime import datetime, timezone

        scrapers = [LoudounScraper(), LCPSScraper()]

        for scraper in scrapers:
            try:
                documents = await scraper.discover_documents()
            except Exception:
                logger.exception("Scraper %s failed", scraper.__class__.__name__)
                continue

            logger.info("%s found %d documents", scraper.__class__.__name__, len(documents))

            for doc in documents:
                # Use pdf_url for download — url is the HTML landing page
                download_url = doc.pdf_url if doc.pdf_url else doc.url

                # Skip non-PDF documents (e.g. BoardDocs HTML pages)
                if not (download_url.lower().endswith(".pdf") or "/edoc/" in download_url.lower()):
                    logger.debug("Skipping non-PDF URL: %s", download_url)
                    await _upsert_meeting_stub(async_session, doc)
                    continue

                # Check if we've already processed this URL
                already_done = await _is_already_processed(async_session, download_url)
                if already_done:
                    logger.debug("Already processed: %s", download_url)
                    continue

                logger.info("Processing: %s", doc.title)

                # ── 1. Download + extract + chunk ─────────────────────────────────
                try:
                    result = await process_pdf(download_url)
                except DownloadError as exc:
                    logger.warning("Download failed for %s: %s", download_url, exc)
                    continue
                except Exception:
                    logger.exception("Process failed for %s", download_url)
                    continue

                if not result.chunks:
                    logger.warning("No chunks from %s, skipping", download_url)
                    continue

                # ── 2. Gemma processing ───────────────────────────────────────────
                rewrites = []
                classifications = []

                for chunk in result.chunks[:30]:  # cap at 30 items per meeting
                    try:
                        rewrite = await rewrite_content(chunk.text)
                        classification = await classify_content(rewrite.summary)
                        rewrites.append(rewrite)
                        classifications.append(classification)
                    except Exception:
                        logger.exception("Gemma failed on chunk")
                        continue

                if not rewrites:
                    logger.warning("No successful Gemma rewrites for %s", doc.title)
                    continue

                # ── 3. Meeting overview ───────────────────────────────────────────
                summaries = [r.summary for r in rewrites]
                try:
                    overview = await generate_meeting_overview(summaries)
                except Exception:
                    logger.exception("Meeting overview failed for %s", doc.title)
                    from backend.llm.models import MeetingOverviewResult
                    overview = MeetingOverviewResult(
                        meeting_overview=" ".join(summaries[:3]),
                        top_decisions=[r.decisions[0] for r in rewrites[:3] if r.decisions],
                        fiscal_total=None,
                        next_meeting_notes=None,
                    )

                # ── 4. DB write ───────────────────────────────────────────────────
                async with async_session() as session:
                    async with session.begin():
                        # Upsert meeting
                        existing = (await session.execute(
                            select(models.Meeting).where(
                                models.Meeting.source_pdf_url == download_url
                            )
                        )).scalar_one_or_none()

                        if existing:
                            meeting = existing
                        else:
                            meeting = models.Meeting(
                                title=doc.title,
                                board_slug=doc.board_type,
                                meeting_date=doc.meeting_date,
                                source_url=doc.url,
                                source_pdf_url=download_url,
                                processing_status="completed",
                            )
                            session.add(meeting)
                            await session.flush()

                        # Update meeting overview
                        meeting.meeting_overview = overview.meeting_overview
                        meeting.top_decisions = overview.top_decisions[:3]
                        meeting.fiscal_total = overview.fiscal_total
                        meeting.next_meeting_notes = overview.next_meeting_notes
                        meeting.processing_status = "completed"

                        # Write agenda items (delete old ones first on re-process)
                        if existing:
                            await session.execute(
                                models.AgendaItem.__table__.delete().where(
                                    models.AgendaItem.meeting_id == meeting.id
                                )
                            )

                        fiscal_count = 0
                        for rewrite, classification in zip(rewrites, classifications):
                            item = models.AgendaItem(
                                meeting_id=meeting.id,
                                title=rewrite.title,
                                summary=rewrite.summary,
                                decisions=rewrite.decisions,
                                action_items=rewrite.action_items,
                                key_figures={
                                    "amounts": rewrite.key_figures.amounts,
                                    "vote_tallies": rewrite.key_figures.vote_tallies,
                                    "dates": rewrite.key_figures.dates,
                                    "schools": rewrite.key_figures.schools,
                                } if rewrite.key_figures else {},
                                primary_category=classification.primary_category,
                                secondary_tags=classification.secondary_tags,
                                urgency=classification.urgency,
                                fiscal_impact=classification.fiscal_impact,
                                affects_schools=classification.affects_schools,
                                source_pdf_url=download_url,
                            )
                            session.add(item)
                            if classification.fiscal_impact:
                                fiscal_count += 1

                        meeting.total_items = len(rewrites)
                        meeting.fiscal_items = fiscal_count

                logger.info(
                    "Wrote meeting %r: %d items, %d fiscal",
                    doc.title, len(rewrites), fiscal_count,
                )

                # Small delay between documents to be courteous to servers
                await asyncio.sleep(2)

        # Bust caches after full cycle
        await invalidate_all_lists()
        await invalidate_search()

    except Exception:
        logger.exception("Scrape cycle failed")
    finally:
        logger.info("Scrape cycle complete")


async def _is_already_processed(session_factory, url: str) -> bool:
    """Return True if this pdf_url is already in the meetings table as completed."""
    from backend.db import models
    from sqlalchemy import select
    async with session_factory() as session:
        row = (await session.execute(
            select(models.Meeting.id).where(
                models.Meeting.source_pdf_url == url,
                models.Meeting.processing_status == "completed",
            ).limit(1)
        )).first()
        return row is not None


async def _upsert_meeting_stub(session_factory, doc) -> None:
    """Insert a meeting record with no agenda items (for HTML-only sources like BoardDocs)."""
    from backend.db import models
    from sqlalchemy import select
    try:
        async with session_factory() as session:
            async with session.begin():
                existing = (await session.execute(
                    select(models.Meeting).where(
                        models.Meeting.board_slug == doc.board_type,
                        models.Meeting.meeting_date == doc.meeting_date,
                    ).limit(1)
                )).scalar_one_or_none()

                if existing:
                    return

                meeting = models.Meeting(
                    title=doc.title,
                    board_slug=doc.board_type,
                    meeting_date=doc.meeting_date,
                    source_url=doc.url,
                    source_pdf_url=doc.pdf_url or doc.url,
                    processing_status="pending",
                    total_items=0,
                    fiscal_items=0,
                )
                session.add(meeting)
    except Exception:
        logger.debug("Could not upsert meeting stub for %s", doc.title)


async def _run() -> None:
    import datetime

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scrape_cycle,
        trigger="interval",
        seconds=POLL_INTERVAL_SECONDS,
        id="scrape_cycle",
        next_run_time=datetime.datetime.now(),
    )
    scheduler.start()
    logger.info(
        "Pipeline worker started — polling every %ds (Ollama: %s, model: %s)",
        POLL_INTERVAL_SECONDS,
        settings.ollama_base_url,
        settings.ollama_model,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _shutdown(sig, _frame):
        logger.info("Received signal %s — shutting down", sig)
        scheduler.shutdown(wait=False)
        loop.call_soon_threadsafe(stop_event.set)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    await stop_event.wait()


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
