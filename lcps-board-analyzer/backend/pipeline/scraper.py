"""Scrapers for lcps.org (BeautifulSoup) and Loudoun County BOS (Legistar API)."""
import logging
import time
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

LCPS_BOARD_URL = "https://go.boarddocs.com/vsba/loudoun/Board.nsf/Public"
LEGISTAR_EVENTS_URL = f"{settings.legistar_base_url}/events"


@dataclass
class DiscoveredDocument:
    url: str
    title: str
    source_type: str  # "lcps" | "loudoun_bos"
    meeting_date: str | None = None


def _polite_get(url: str, client: httpx.Client) -> httpx.Response:
    """GET with browser headers + polite delay."""
    time.sleep(settings.pipeline_request_delay)
    response = client.get(url, headers=BROWSER_HEADERS, follow_redirects=True, timeout=30)
    response.raise_for_status()
    return response


def scrape_lcps(client: httpx.Client) -> list[DiscoveredDocument]:
    """Scrape LCPS BoardDocs page for PDF links to board meeting agendas and minutes."""
    documents: list[DiscoveredDocument] = []
    try:
        response = _polite_get(LCPS_BOARD_URL, client)
        soup = BeautifulSoup(response.text, "html.parser")
        # BoardDocs lists meetings as links — find all anchors pointing to PDFs or meeting pages
        for a in soup.find_all("a", href=True):
            href: str = a["href"]
            if ".pdf" in href.lower() or "agenda" in href.lower() or "minutes" in href.lower():
                full_url = href if href.startswith("http") else f"https://go.boarddocs.com{href}"
                documents.append(
                    DiscoveredDocument(
                        url=full_url,
                        title=a.get_text(strip=True) or "LCPS Board Document",
                        source_type="lcps",
                    )
                )
        logger.info("LCPS scraper found %d documents", len(documents))
    except Exception as exc:
        logger.error("LCPS scraper failed: %s", exc)
    return documents


def scrape_loudoun_bos(client: httpx.Client) -> list[DiscoveredDocument]:
    """Fetch Loudoun County BOS events via Legistar API — structured JSON, no scraping."""
    documents: list[DiscoveredDocument] = []
    try:
        time.sleep(settings.pipeline_request_delay)
        response = client.get(
            LEGISTAR_EVENTS_URL,
            params={"$top": 10, "$orderby": "EventDate desc"},
            timeout=30,
        )
        response.raise_for_status()
        events = response.json()
        for event in events:
            event_id = event.get("EventId")
            event_date = event.get("EventDate", "")[:10]
            # Each event may link to an agenda PDF
            agenda_url = event.get("EventAgendaFile") or event.get("EventMinutesFile")
            if agenda_url:
                documents.append(
                    DiscoveredDocument(
                        url=agenda_url,
                        title=f"Loudoun BOS Meeting — {event_date}",
                        source_type="loudoun_bos",
                        meeting_date=event_date,
                    )
                )
        logger.info("Loudoun BOS Legistar API found %d documents", len(documents))
    except Exception as exc:
        logger.error("Loudoun BOS scraper failed: %s", exc)
    return documents


def discover_all_documents() -> list[DiscoveredDocument]:
    """Run all scrapers and return combined list of discovered documents."""
    with httpx.Client() as client:
        lcps_docs = scrape_lcps(client)
        bos_docs = scrape_loudoun_bos(client)
    return lcps_docs + bos_docs
