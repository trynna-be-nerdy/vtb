"""Tests for backend/pipeline/scrapers/"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.pipeline.scrapers.base import DocumentInfo, _RATE_LIMIT_SECONDS
from backend.pipeline.scrapers.lcps_scraper import (
    LCPSScraper,
    _extract_pdf_url,
    _parse_boarddocs_date,
)
from backend.pipeline.scrapers.loudoun_scraper import (
    LoudounScraper,
    _map_board_type,
    _parse_legistar_date,
)


# ── DocumentInfo ────────────────────────────────────────────────────────────

def test_document_info_compute_hash():
    doc = DocumentInfo(
        url="https://example.gov/meeting",
        pdf_url="https://example.gov/agenda.pdf",
        title="Test Meeting",
        meeting_date=date(2024, 5, 14),
        board_type="lcps",
    )
    content = b"some pdf bytes"
    doc.compute_hash(content)
    import hashlib
    assert doc.sha256_hash == hashlib.sha256(content).hexdigest()


# ── BoardDocs date parsing ──────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("05/14/2024", date(2024, 5, 14)),
    ("2024-05-14", date(2024, 5, 14)),
    ("", None),
    ("not-a-date", None),
])
def test_parse_boarddocs_date(raw, expected):
    assert _parse_boarddocs_date(raw) == expected


# ── PDF extraction from HTML ────────────────────────────────────────────────

def test_extract_pdf_url_finds_boarddocs_path():
    html = '<a href="/va/lcps/Board.nsf/files/abc123/$file/agenda.pdf">Agenda</a>'
    result = _extract_pdf_url(html)
    assert result and "agenda.pdf" in result
    assert result.startswith("https://go.boarddocs.com")


def test_extract_pdf_url_finds_generic_link():
    html = '<a href="https://example.gov/docs/meeting.pdf">Download</a>'
    result = _extract_pdf_url(html)
    assert result == "https://example.gov/docs/meeting.pdf"


def test_extract_pdf_url_returns_none_when_no_pdf():
    html = "<html><body><p>No PDF here</p></body></html>"
    assert _extract_pdf_url(html) is None


# ── Legistar date parsing ───────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected", [
    ("2024-05-14T00:00:00", date(2024, 5, 14)),
    ("2024-05-14", date(2024, 5, 14)),
    ("", None),
    ("bad", None),
])
def test_parse_legistar_date(raw, expected):
    assert _parse_legistar_date(raw) == expected


# ── Board type mapping ──────────────────────────────────────────────────────

@pytest.mark.parametrize("name,expected", [
    ("Board of Supervisors", "supervisors"),
    ("Planning Commission", "planning"),
    ("Advisory Committee", "advisory"),
    ("Unknown Body", "advisory"),
])
def test_map_board_type(name, expected):
    assert _map_board_type(name) == expected


# ── LCPSScraper ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_lcps_scraper_discover_documents():
    meetings_data = [
        {"unique": "abc123", "date": "05/14/2024", "name": "Regular Board Meeting"},
        {"unique": "def456", "date": "04/09/2024", "name": "Special Session"},
    ]
    agenda_html = '<a href="/va/lcps/Board.nsf/files/abc/$file/agenda.pdf">PDF</a>'

    scraper = LCPSScraper()

    mock_meetings_resp = MagicMock()
    mock_meetings_resp.json.return_value = meetings_data
    mock_meetings_resp.text = ""

    mock_agenda_resp = MagicMock()
    mock_agenda_resp.text = agenda_html
    mock_agenda_resp.json.return_value = {}

    call_count = 0

    async def mock_get(url, **kwargs):
        nonlocal call_count
        call_count += 1
        if "getmeetings" in url:
            return mock_meetings_resp
        return mock_agenda_resp

    with patch.object(scraper, "_get", side_effect=mock_get):
        docs = await scraper.discover_documents()

    assert len(docs) == 2
    assert all(isinstance(d, DocumentInfo) for d in docs)
    assert all(d.board_type == "lcps" for d in docs)
    assert docs[0].meeting_date == date(2024, 5, 14)


@pytest.mark.asyncio
async def test_lcps_scraper_falls_back_to_playwright_on_failure():
    scraper = LCPSScraper()

    async def failing_get(url, **kwargs):
        raise Exception("network error")

    fallback_doc = DocumentInfo(
        url="https://example.gov/fallback.pdf",
        pdf_url="https://example.gov/fallback.pdf",
        title="Fallback Doc",
        meeting_date=date(2024, 1, 1),
        board_type="lcps",
    )

    with patch.object(scraper, "_get", side_effect=failing_get):
        with patch(
            "backend.pipeline.scrapers.lcps_scraper.scrape_with_playwright",
            new_callable=AsyncMock,
            return_value=[fallback_doc],
        ):
            docs = await scraper.discover_documents()

    assert docs == [fallback_doc]


# ── LoudounScraper ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_loudoun_scraper_discover_documents():
    events_data = [
        {
            "EventId": 1001,
            "EventDate": "2024-05-14T00:00:00",
            "EventBodyName": "Board of Supervisors",
            "EventAgendaStatusName": "Final",
            "EventAgendaFile": "https://loudoun.legistar.com/View.ashx?M=A&ID=1001",
            "EventMinutesFile": None,
            "EventInSiteURL": "https://loudoun.legistar.com/MeetingDetail.aspx?ID=1001",
        }
    ]

    scraper = LoudounScraper()

    mock_resp = MagicMock()
    mock_resp.json.return_value = events_data

    with patch.object(scraper, "_get", AsyncMock(return_value=mock_resp)):
        docs = await scraper.discover_documents()

    assert len(docs) == 1
    assert docs[0].board_type == "supervisors"
    assert docs[0].meeting_date == date(2024, 5, 14)
    assert "loudoun.legistar.com" in docs[0].pdf_url


@pytest.mark.asyncio
async def test_loudoun_scraper_skips_event_without_pdf():
    events_data = [
        {
            "EventId": 2002,
            "EventDate": "2024-06-01T00:00:00",
            "EventBodyName": "Planning Commission",
            "EventAgendaFile": None,
            "EventMinutesFile": None,
            "EventInSiteURL": None,
        }
    ]

    scraper = LoudounScraper()

    mock_resp = MagicMock()
    mock_resp.json.return_value = events_data

    # Attachment lookup also returns nothing
    mock_items_resp = MagicMock()
    mock_items_resp.json.return_value = []

    call_num = 0

    async def mock_get(url, **kwargs):
        nonlocal call_num
        call_num += 1
        if "eventitems" in url:
            return mock_items_resp
        return mock_resp

    with patch.object(scraper, "_get", side_effect=mock_get):
        docs = await scraper.discover_documents()

    assert docs == []
