"""
LCPS BoardDocs scraper.

BoardDocs exposes an undocumented-but-stable JSON API used by its own JS frontend.
We hit those JSON endpoints directly; Playwright fallback is invoked if they fail.
"""

import logging
import re
from datetime import date, datetime
from typing import Any

from bs4 import BeautifulSoup

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

_BOARDDOCS_BASE = "https://go.boarddocs.com/va/lcps/Board.nsf"
_MEETINGS_URL = f"{_BOARDDOCS_BASE}/getmeetings?open"
_AGENDA_URL = f"{_BOARDDOCS_BASE}/getAgenda?open"
_BOOK_URL = f"{_BOARDDOCS_BASE}/GetCurrentBook?open"

# BoardDocs attaches the agenda PDF as a document in the meeting's "book" object.
# PDF links follow the pattern: /va/lcps/Board.nsf/files/<id>/$file/<filename>.pdf
_PDF_RE = re.compile(r"/va/lcps/Board\.nsf/files/[^\"']+\.pdf", re.IGNORECASE)


class LCPSScraper(BaseScraper):
    """Discover LCPS board meeting agenda PDFs from BoardDocs."""

    async def discover_documents(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []
        try:
            meetings = await self._fetch_meetings()
        except Exception as exc:
            logger.warning("BoardDocs meetings fetch failed (%s), trying Playwright", exc)
            from .playwright_fallback import scrape_with_playwright
            return await scrape_with_playwright(_BOARDDOCS_BASE, board_type="lcps")

        for meeting in meetings:
            try:
                doc = await self._process_meeting(meeting)
                if doc:
                    docs.append(doc)
            except Exception as exc:
                logger.warning("Skipping meeting %s: %s", meeting.get("unique"), exc)

        logger.info("LCPSScraper discovered %d documents", len(docs))
        return docs

    async def _fetch_meetings(self) -> list[dict[str, Any]]:
        resp = await self._get(_MEETINGS_URL, json=True)
        data = resp.json()
        # BoardDocs returns either a list directly or {"meetings": [...]}
        if isinstance(data, list):
            return data
        return data.get("meetings", [])

    async def _process_meeting(self, meeting: dict[str, Any]) -> DocumentInfo | None:
        unique = meeting.get("unique") or meeting.get("id")
        if not unique:
            return None

        raw_date = meeting.get("date") or meeting.get("startDate") or ""
        meeting_date = _parse_boarddocs_date(raw_date)
        if not meeting_date:
            return None

        title = meeting.get("name") or meeting.get("title") or f"LCPS Meeting {raw_date}"

        # Fetch the agenda page to find the PDF attachment link
        agenda_url = f"{_AGENDA_URL}&id={unique}"
        try:
            resp = await self._get(agenda_url)
            pdf_url = _extract_pdf_url(resp.text)
        except Exception:
            pdf_url = None

        if not pdf_url:
            # Fall back to the meeting landing page
            landing = f"{_BOARDDOCS_BASE}/Public/{unique}?open"
            pdf_url = landing  # best guess — downloader will validate MIME type

        return DocumentInfo(
            url=f"{_BOARDDOCS_BASE}/Public/{unique}?open",
            pdf_url=pdf_url,
            title=title,
            meeting_date=meeting_date,
            board_type="lcps",
        )


def _parse_boarddocs_date(raw: str) -> date | None:
    """Parse BoardDocs date strings: 'MM/DD/YYYY', 'YYYY-MM-DD', epoch ms int."""
    if not raw:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y"):
        try:
            return datetime.strptime(str(raw).strip(), fmt).date()
        except ValueError:
            continue
    # Epoch milliseconds (integer)
    try:
        return date.fromtimestamp(int(raw) / 1000)
    except (ValueError, TypeError, OSError):
        return None


def _extract_pdf_url(html: str) -> str | None:
    """Find the first .pdf link in BoardDocs HTML/JSON response."""
    match = _PDF_RE.search(html)
    if match:
        return f"https://go.boarddocs.com{match.group(0)}"
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all("a", href=True):
        href: str = tag["href"]
        if href.lower().endswith(".pdf"):
            if href.startswith("http"):
                return href
            return f"https://go.boarddocs.com{href}"
    return None
