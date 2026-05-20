"""
LCPS School Board scraper.

Uses the BoardDocs internal API endpoint:
  GET https://go.boarddocs.com/vsba/loudoun/Board.nsf/BD-GetMeetingsList?open

Returns JSON with meeting IDs and dates. We then fetch the agenda for each
meeting via the getAgenda endpoint.
"""

import logging
import random
import re
from datetime import date, datetime

import httpx
from playwright.async_api import async_playwright

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

_BD_BASE     = "https://go.boarddocs.com/vsba/loudoun/Board.nsf"
_BD_PUBLIC   = f"{_BD_BASE}/Public"
_BOARD_TYPE  = "lcps-school-board"

# Only scrape these meeting types (skip committee/closed meetings)
_INCLUDE_TYPES = [
    "school board meeting",
    "business meeting",
    "2nd tuesday",
    "4th tuesday",
    "special school board",
    "annual meeting",
    "work session",
]

_EXCLUDE_TYPES = [
    "committee",
    "closed",
    "cancelled",
    "cancel",
    "closed session only",
]


def _parse_numberdate(nd: str) -> date | None:
    """Parse BoardDocs numberdate format YYYYMMDD."""
    try:
        return datetime.strptime(nd[:8], "%Y%m%d").date()
    except (ValueError, TypeError):
        return None


def _is_full_board_meeting(name: str) -> bool:
    lower = name.lower()
    if any(x in lower for x in _EXCLUDE_TYPES):
        return False
    return any(x in lower for x in _INCLUDE_TYPES)


def _day_str(d: date) -> str:
    return f"{d.strftime('%B')} {d.day}, {d.year}"


class LCPSScraper(BaseScraper):
    """Discover LCPS school board meeting agendas via BoardDocs API."""

    async def discover_documents(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []
        try:
            docs = await self._scrape_via_api()
        except Exception:
            logger.exception("LCPSScraper API scrape failed")
        logger.info("LCPSScraper discovered %d documents", len(docs))
        return docs

    async def _scrape_via_api(self) -> list[DocumentInfo]:
        """Use BoardDocs internal API to get meeting list, then fetch agendas."""
        docs: list[DocumentInfo] = []
        meetings_json: list[dict] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Intercept the BD-GetMeetingsList response that fires when MEETINGS is clicked
            captured: list[dict] = []

            async def handle_response(resp):
                if "BD-GetMeetingsList" in resp.url and resp.status == 200:
                    try:
                        text = await resp.text()
                        import json as _json
                        data = _json.loads(text)
                        if isinstance(data, list):
                            captured.extend(data)
                            logger.info("Captured %d meetings from BD API", len(data))
                    except Exception:
                        pass

            page.on("response", handle_response)

            await page.goto(_BD_PUBLIC, wait_until="networkidle", timeout=30_000)
            await page.wait_for_timeout(1500)

            # Click the MEETINGS tab to trigger the API call
            try:
                await page.locator("#li-meetings, a:has-text('MEETINGS'), [data-tab='meetings']").first.click(timeout=8000)
                await page.wait_for_timeout(3000)
            except Exception:
                logger.warning("Could not click MEETINGS tab, trying JS click")
                try:
                    await page.evaluate("document.querySelector('#li-meetings a, #tab-meetings').click()")
                    await page.wait_for_timeout(3000)
                except Exception:
                    pass

            meetings_json = captured
            logger.info("Total meetings captured: %d", len(meetings_json))

            if not meetings_json:
                logger.warning("No meetings captured from BoardDocs API")
                await browser.close()
                return []
            logger.info("BoardDocs returned %d meeting entries", len(meetings_json))

            # Filter to recent full-board meetings (last 2 years)
            from datetime import date as _date
            cutoff = _date(today := _date.today(), today.year - 2, today.month, today.day)
            try:
                cutoff = _date(today.year - 2, today.month, today.day)
            except ValueError:
                cutoff = _date(today.year - 2, 1, 1)

            eligible = []
            for m in meetings_json:
                nd = m.get("numberdate", "")
                meeting_date = _parse_numberdate(nd)
                if not meeting_date:
                    continue
                if meeting_date < cutoff:
                    continue
                name = m.get("name", "")
                if not _is_full_board_meeting(name):
                    continue
                eligible.append((meeting_date, name, m.get("unique", "")))

            eligible.sort(reverse=True)
            logger.info("Eligible full-board meetings: %d", len(eligible))

            for meeting_date, name, unique_id in eligible[:40]:
                if not unique_id:
                    continue

                # Fetch the agenda for this meeting
                agenda_url = f"{_BD_BASE}/getAgenda?open&id={unique_id}"
                try:
                    agenda_resp = await page.request.get(agenda_url, headers={"Referer": _BD_PUBLIC})
                    agenda_text = await agenda_resp.text() if agenda_resp.status == 200 else ""
                except Exception:
                    agenda_text = ""

                # BoardDocs doesn't serve standalone PDFs — the agenda IS the page
                meeting_title = f"LCPS School Board {name.strip()} – {_day_str(meeting_date)}"
                landing_url = f"{_BD_BASE}/Pub?open&id={unique_id}"

                docs.append(DocumentInfo(
                    url=landing_url,
                    pdf_url=landing_url,  # BoardDocs agendas are HTML, not PDFs
                    title=meeting_title,
                    meeting_date=meeting_date,
                    board_type=_BOARD_TYPE,
                ))

                # Small rate limit
                await page.wait_for_timeout(300)

            await browser.close()

        return docs
