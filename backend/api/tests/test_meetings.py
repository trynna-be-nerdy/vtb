"""Tests for GET /api/meetings and GET /api/meetings/{id}"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.api.schemas import MeetingCard, AgendaItemDetail, SupportingDocumentOut
from backend.api.tests.conftest import make_meeting, make_agenda_item


# ── GET /api/meetings ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_meetings_returns_200(client, mock_db):
    meeting = make_meeting()
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [meeting]

    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    resp = await client.get("/api/meetings")
    assert resp.status_code == 200
    data = resp.json()
    assert "meetings" in data
    assert "pagination" in data
    assert len(data["meetings"]) == 1
    assert data["meetings"][0]["title"] == "Regular Board Meeting"


@pytest.mark.asyncio
async def test_list_meetings_pagination(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 50
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [make_meeting(id=i) for i in range(1, 21)]

    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    resp = await client.get("/api/meetings?page=1&limit=20")
    assert resp.status_code == 200
    data = resp.json()
    assert data["pagination"]["total"] == 50
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["page"] == 1


@pytest.mark.asyncio
async def test_list_meetings_last_page_has_next_false(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 3
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [make_meeting(id=i) for i in range(1, 4)]

    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    resp = await client.get("/api/meetings?page=1&limit=20")
    assert resp.status_code == 200
    assert resp.json()["pagination"]["has_next"] is False


@pytest.mark.asyncio
async def test_list_meetings_filter_by_board(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    supervisors_meeting = make_meeting(board_slug="supervisors")
    list_result.scalars.return_value.all.return_value = [supervisors_meeting]

    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    resp = await client.get("/api/meetings?board=supervisors")
    assert resp.status_code == 200
    data = resp.json()
    assert data["meetings"][0]["board_slug"] == "supervisors"


@pytest.mark.asyncio
async def test_list_meetings_empty_returns_empty_list(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = []

    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    resp = await client.get("/api/meetings")
    assert resp.status_code == 200
    assert resp.json()["meetings"] == []
    assert resp.json()["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_list_meetings_served_from_cache(client, mock_db, patch_cache):
    cached_payload = {
        "meetings": [{"id": 99, "title": "Cached Meeting"}],
        "pagination": {"page": 1, "limit": 20, "total": 1, "has_next": False},
    }
    patch_cache["get"].return_value = cached_payload

    resp = await client.get("/api/meetings")
    assert resp.status_code == 200
    assert resp.json()["meetings"][0]["id"] == 99
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_list_meetings_sets_cache_on_miss(client, mock_db, patch_cache):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    list_result = MagicMock()
    list_result.scalars.return_value.all.return_value = [make_meeting()]
    mock_db.execute = AsyncMock(side_effect=[count_result, list_result])

    await client.get("/api/meetings")
    patch_cache["set"].assert_called_once()


# ── GET /api/meetings/{id} ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_meeting_returns_detail(client, mock_db):
    meeting = make_meeting(id=1)
    meeting.agenda_items = [make_agenda_item()]
    meeting.supporting_documents = []

    detail_result = MagicMock()
    detail_result.scalar_one_or_none.return_value = meeting
    mock_db.execute = AsyncMock(return_value=detail_result)

    resp = await client.get("/api/meetings/1")
    assert resp.status_code == 200
    data = resp.json()
    assert "meeting" in data
    assert data["meeting"]["id"] == 1
    assert "agenda_items" in data["meeting"]


@pytest.mark.asyncio
async def test_get_meeting_returns_404_when_not_found(client, mock_db):
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    mock_db.execute = AsyncMock(return_value=result)

    resp = await client.get("/api/meetings/9999")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Meeting not found"


@pytest.mark.asyncio
async def test_get_meeting_includes_agenda_items(client, mock_db):
    meeting = make_meeting(id=1)
    meeting.agenda_items = [make_agenda_item(id=1), make_agenda_item(id=2)]
    meeting.supporting_documents = []

    result = MagicMock()
    result.scalar_one_or_none.return_value = meeting
    mock_db.execute = AsyncMock(return_value=result)

    resp = await client.get("/api/meetings/1")
    assert resp.status_code == 200
    assert len(resp.json()["meeting"]["agenda_items"]) == 2


@pytest.mark.asyncio
async def test_get_meeting_served_from_cache(client, mock_db, patch_cache):
    patch_cache["get"].return_value = {
        "meeting": {"id": 42, "title": "Cached Detail Meeting"}
    }

    resp = await client.get("/api/meetings/42")
    assert resp.status_code == 200
    assert resp.json()["meeting"]["id"] == 42
    mock_db.execute.assert_not_called()
