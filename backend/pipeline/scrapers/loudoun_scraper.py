"""
Loudoun County scraper using the Legistar JSON API.

Legistar is well-documented and returns structured data — no HTML parsing needed.
API base: https://webapi.legistar.com/v1/loudouncounty
"""

import logging
from datetime import date, datetime
from typing import Any

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

_API_BASE = "https://webapi.legistar.com/v1/loudouncounty"

# Board of Supervisors body ID in Loudoun Legistar (1 = default BOS)
# Planning Commission is typically body ID 2; we fetch the top-N recent events.
_RECENT_EVENTS = 50  # how many past events to fetch per request

# Board type mapping keyed by Legistar EventBodyName substrings
_BOARD_TYPE_MAP: list[tuple[str, str]] = [
    ("supervisor", "supervisors"),
    ("planning", "planning"),
    ("advisory", "advisory"),
]


class LoudounScraper(BaseScraper):
    """Discover Loudoun County meeting agenda PDFs from the Legistar API."""

    async def discover_documents(self) -> list[DocumentInfo]:
        events = await self._fetch_recent_events()
        docs: list[DocumentInfo] = []

        for event in events:
            try:
                doc = await self._process_event(event)
                if doc:
                    docs.append(doc)
            except Exception as exc:
                logger.warning("Skipping Legistar event %s: %s", event.get("EventId"), exc)

        logger.info("LoudounScraper discovered %d documents", len(docs))
        return docs

    async def _fetch_recent_events(self) -> list[dict[str, Any]]:
        # Legistar API returns 500 with OData string-filter; use unfiltered endpoint
        url = (
            f"{_API_BASE}/events"
            f"?$top={_RECENT_EVENTS}"
            f"&$orderby=EventDate desc"
        )
        resp = await self._get(url, json=True)
        events = resp.json()
        # Filter client-side: only keep events that have a published agenda
        return [
            e for e in events
            if e.get("EventAgendaStatusName") in ("Final", "Final Revised", "Published")
            or e.get("EventAgendaFile")
        ]

    async def _process_event(self, event: dict[str, Any]) -> DocumentInfo | None:
        event_id = event.get("EventId")
        if not event_id:
            return None

        raw_date = event.get("EventDate", "")
        meeting_date = _parse_legistar_date(raw_date)
        if not meeting_date:
            return None

        body_name: str = event.get("EventBodyName") or ""
        board_type = _map_board_type(body_name)
        title = f"{body_name} – {meeting_date.isoformat()}"

        # Legistar stores agenda as a document attachment
        agenda_file = event.get("EventAgendaFile")  # may be a URL already
        minutes_file = event.get("EventMinutesFile")

        pdf_url = agenda_file or minutes_file
        if not pdf_url:
            pdf_url = await self._find_agenda_attachment(event_id)

        if not pdf_url:
            logger.debug("No PDF for event %s (%s), skipping", event_id, title)
            return None

        # Normalise relative Legistar paths
        if pdf_url and not pdf_url.startswith("http"):
            pdf_url = f"https://loudoun.legistar.com{pdf_url}"

        landing_url = event.get("EventInSiteURL") or f"https://loudoun.legistar.com/MeetingDetail.aspx?ID={event_id}"

        return DocumentInfo(
            url=landing_url,
            pdf_url=pdf_url,
            title=title,
            meeting_date=meeting_date,
            board_type=board_type,
        )

    async def _find_agenda_attachment(self, event_id: int) -> str | None:
        """Check event media files endpoint for a PDF agenda."""
        url = f"{_API_BASE}/events/{event_id}/eventitems?$expand=EventItemAttachments"
        try:
            resp = await self._get(url, json=True)
            items = resp.json()
        except Exception:
            return None

        for item in items:
            for att in item.get("EventItemAttachments") or []:
                href: str = att.get("MatterAttachmentHyperlink") or ""
                if href.lower().endswith(".pdf"):
                    return href
        return None


def _parse_legistar_date(raw: str) -> date | None:
    """Parse Legistar ISO-8601 date strings like '2024-05-14T00:00:00'."""
    if not raw:
        return None
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw[:19], fmt).date()
        except ValueError:
            continue
    return None


def _map_board_type(body_name: str) -> str:
    lower = body_name.lower()
    for fragment, slug in _BOARD_TYPE_MAP:
        if fragment in lower:
            return slug
    return "advisory"
