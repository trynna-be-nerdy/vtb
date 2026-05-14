"""
Playwright-based fallback scraper for JS-heavy government pages.

Only imported and invoked when the primary HTTP scraper fails.
Requires: playwright (install separately: `pip install playwright && playwright install chromium`)
"""

import logging
import re
from datetime import date, datetime
from typing import Any

from .base import DocumentInfo

logger = logging.getLogger(__name__)

_PDF_RE = re.compile(r'https?://[^\s"\']+\.pdf', re.IGNORECASE)


async def scrape_with_playwright(
    url: str,
    board_type: str = "lcps",
    *,
    timeout_ms: int = 30_000,
) -> list[DocumentInfo]:
    """Load *url* in a headless Chromium browser and extract PDF links.

    Returns an empty list (instead of raising) if Playwright is not installed,
    so the pipeline degrades gracefully.
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning(
            "playwright not installed — JS-heavy scraping unavailable. "
            "Run: pip install playwright && playwright install chromium"
        )
        return []

    docs: list[DocumentInfo] = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            await page.goto(url, timeout=timeout_ms, wait_until="networkidle")
            content = await page.content()

            pdf_urls = list(dict.fromkeys(_PDF_RE.findall(content)))  # deduplicate, preserve order
            logger.info("Playwright found %d PDF URLs on %s", len(pdf_urls), url)

            for pdf_url in pdf_urls:
                doc = _pdf_url_to_document_info(pdf_url, board_type)
                if doc:
                    docs.append(doc)

        except Exception as exc:
            logger.error("Playwright scrape of %s failed: %s", url, exc)
        finally:
            await browser.close()

    return docs


def _pdf_url_to_document_info(pdf_url: str, board_type: str) -> DocumentInfo | None:
    """Best-effort DocumentInfo from a bare PDF URL (no meeting metadata available)."""
    # Try to extract a date from the URL (common in government filenames)
    meeting_date = _extract_date_from_url(pdf_url) or date.today()
    title = pdf_url.split("/")[-1].replace(".pdf", "").replace("-", " ").replace("_", " ").title()
    return DocumentInfo(
        url=pdf_url,
        pdf_url=pdf_url,
        title=title or "Meeting Agenda",
        meeting_date=meeting_date,
        board_type=board_type,
    )


def _extract_date_from_url(url: str) -> date | None:
    for pattern in (
        r"(\d{4})[_\-](\d{2})[_\-](\d{2})",
        r"(\d{2})[_\-](\d{2})[_\-](\d{4})",
    ):
        m = re.search(pattern, url)
        if not m:
            continue
        groups = m.groups()
        for fmt_groups, fmt in [
            ((groups[0], groups[1], groups[2]), "%Y-%m-%d"),
            ((groups[2], groups[0], groups[1]), "%Y-%m-%d"),
        ]:
            try:
                return datetime.strptime(f"{fmt_groups[0]}-{fmt_groups[1]}-{fmt_groups[2]}", fmt).date()
            except ValueError:
                continue
    return None
