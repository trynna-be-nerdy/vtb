"""
Loudoun County Board of Supervisors scraper.

Uses Playwright to load the Loudoun Legistar calendar (loudoun.legistar.com)
because the Legistar JSON API returns 500 for all Loudoun County endpoints
and the loudoun.gov portal requires JavaScript to render meeting data.
"""

import logging
import re
from datetime import date, datetime
from typing import Any

from playwright.async_api import async_playwright

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

_LEGISTAR_CALENDAR = "https://loudoun.legistar.com/Calendar.aspx"

# Map Legistar body name substrings → our board slugs
_BOARD_TYPE_MAP: list[tuple[str, str]] = [
    ("supervisor", "board-of-supervisors"),
    ("planning",   "planning-commission"),
    ("advisory",   "advisory-boards"),
]


def _map_board_type(body_name: str) -> str:
    lower = body_name.lower()
    for fragment, slug in _BOARD_TYPE_MAP:
        if fragment in lower:
            return slug
    return "advisory-boards"


def _parse_date(raw: str) -> date | None:
    for fmt in ("%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


class LoudounScraper(BaseScraper):
    """Discover Loudoun County meeting agendas via Playwright on legistar.com."""

    async def discover_documents(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []
        try:
            docs = await self._scrape_with_playwright()
        except Exception:
            logger.exception("LoudounScraper Playwright scrape failed")
        logger.info("LoudounScraper discovered %d documents", len(docs))
        return docs

    async def _scrape_with_playwright(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            page.set_default_timeout(30_000)

            # Load the Legistar calendar and wait for the meeting table
            await page.goto(_LEGISTAR_CALENDAR, wait_until="networkidle")

            # Legistar calendar table rows
            rows = await page.query_selector_all("table#ctl00_ContentPlaceHolder1_gridCalendar_ctl00 tbody tr")
            if not rows:
                # Try the generic table selector
                rows = await page.query_selector_all("table.rgMasterTable tbody tr")

            for row in rows:
                try:
                    doc = await self._parse_row(row)
                    if doc:
                        docs.append(doc)
                except Exception as exc:
                    logger.debug("Skipping row: %s", exc)

            await browser.close()

        return docs

    async def _parse_row(self, row: Any) -> DocumentInfo | None:
        cells = await row.query_selector_all("td")
        if len(cells) < 4:
            return None

        body_name = (await cells[0].inner_text()).strip()
        date_str  = (await cells[1].inner_text()).strip()
        time_str  = (await cells[2].inner_text()).strip()

        meeting_date = _parse_date(date_str)
        if not meeting_date:
            return None

        board_type = _map_board_type(body_name)
        title = f"{body_name} – {meeting_date.strftime('%B %-d, %Y')}"

        # Look for an agenda PDF link in the row
        pdf_url: str | None = None
        landing_url: str | None = None

        links = await row.query_selector_all("a")
        for link in links:
            href = await link.get_attribute("href") or ""
            text = (await link.inner_text()).strip().lower()
            if "agenda" in text or href.lower().endswith(".pdf"):
                if href.startswith("http"):
                    pdf_url = href
                elif href:
                    pdf_url = f"https://loudoun.legistar.com/{href.lstrip('/')}"
            if "meetingdetail" in href.lower() or "detail" in text:
                if href.startswith("http"):
                    landing_url = href
                elif href:
                    landing_url = f"https://loudoun.legistar.com/{href.lstrip('/')}"

        if not pdf_url and not landing_url:
            return None

        return DocumentInfo(
            url=landing_url or f"https://loudoun.legistar.com/Calendar.aspx",
            pdf_url=pdf_url or "",
            title=title,
            meeting_date=meeting_date,
            board_type=board_type,
        )
