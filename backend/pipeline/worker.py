"""
Pipeline worker — runs on a schedule via APScheduler.

Scrapes Loudoun County and LCPS portals for new meeting documents, processes
each PDF through the pipeline, writes results to the database, and publishes
real-time notifications via Redis Pub/Sub.

Start with:
    python -m backend.pipeline.worker
"""

import asyncio
import logging
import signal
import sys

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from backend.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

# How often to poll for new documents (seconds)
POLL_INTERVAL_SECONDS = 3600  # every hour


async def run_scrape_cycle() -> None:
    """One scrape cycle: discover new documents and process each one."""
    logger.info("Scrape cycle started")
    try:
        from backend.pipeline.scrapers.loudoun_scraper import LoudounScraper
        from backend.pipeline.scrapers.lcps_scraper import LCPSScraper
        from backend.pipeline import process_pdf
        from backend.pubsub import publish_new_item
        from backend.cache.invalidator import invalidate_all_lists, invalidate_search
        from backend.db.database import async_session as AsyncSessionLocal
        from backend.db import models

        scrapers = [LoudounScraper(), LCPSScraper()]

        for scraper in scrapers:
            try:
                documents = await scraper.discover()
            except Exception:
                logger.exception("Scraper %s failed during discover", scraper.__class__.__name__)
                continue

            for doc in documents:
                try:
                    result = await process_pdf(doc.url)
                    logger.info(
                        "Processed %s: %d chunks from %d pages",
                        doc.url, len(result.chunks), result.page_count,
                    )
                    # Publish real-time notification after successful processing
                    await publish_new_item(
                        meeting_id=doc.meeting_id,
                        item_id=doc.item_id,
                        title=doc.title,
                        category=doc.category,
                    )
                except Exception:
                    logger.exception("Failed to process document %s", doc.url)

        # Bust all list/feed/search caches after full scrape cycle
        await invalidate_all_lists()
        await invalidate_search()

    except Exception:
        logger.exception("Scrape cycle failed")
    finally:
        logger.info("Scrape cycle complete")


async def _run() -> None:
    import datetime

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        run_scrape_cycle,
        trigger="interval",
        seconds=POLL_INTERVAL_SECONDS,
        id="scrape_cycle",
        next_run_time=datetime.datetime.now(),  # run immediately on start
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
