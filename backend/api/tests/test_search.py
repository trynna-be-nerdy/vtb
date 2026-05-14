"""Tests for GET /api/search"""

from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.api.tests.conftest import make_agenda_item


def _make_search_row(item_id: int = 1, rank: float = 0.75) -> MagicMock:
    row = MagicMock()
    item = make_agenda_item(id=item_id)
    row.AgendaItem = item
    row.meeting_title = "Regular Board Meeting"
    row.meeting_date = date(2024, 5, 14)
    row.board_slug = "lcps"
    row.rank = rank
    return row


# ── Basic search ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_returns_200(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    rows_result = MagicMock()
    rows_result.all.return_value = [_make_search_row()]
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    resp = await client.get("/api/search?q=budget")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "budget"
    assert len(data["results"]) == 1


@pytest.mark.asyncio
async def test_search_result_has_required_fields(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    rows_result = MagicMock()
    rows_result.all.return_value = [_make_search_row(rank=0.92)]
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    resp = await client.get("/api/search?q=school")
    result = resp.json()["results"][0]
    assert "meeting_title" in result
    assert "meeting_date" in result
    assert "board_slug" in result
    assert "rank" in result
    assert isinstance(result["rank"], float)


@pytest.mark.asyncio
async def test_search_results_ranked(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 2
    rows_result = MagicMock()
    rows_result.all.return_value = [
        _make_search_row(item_id=1, rank=0.95),
        _make_search_row(item_id=2, rank=0.40),
    ]
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    resp = await client.get("/api/search?q=safety")
    results = resp.json()["results"]
    assert results[0]["rank"] >= results[1]["rank"]


@pytest.mark.asyncio
async def test_search_empty_results(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    rows_result = MagicMock()
    rows_result.all.return_value = []
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    resp = await client.get("/api/search?q=xyzzy")
    assert resp.status_code == 200
    assert resp.json()["results"] == []
    assert resp.json()["pagination"]["total"] == 0


# ── Query validation ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_rejects_empty_query(client, mock_db):
    resp = await client.get("/api/search?q=")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_rejects_single_char_query(client, mock_db):
    resp = await client.get("/api/search?q=a")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_accepts_two_char_query(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    rows_result = MagicMock()
    rows_result.all.return_value = []
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    resp = await client.get("/api/search?q=ab")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_search_requires_q_param(client, mock_db):
    resp = await client.get("/api/search")
    assert resp.status_code == 422


# ── Pagination ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_pagination(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 100
    rows_result = MagicMock()
    rows_result.all.return_value = [_make_search_row(i) for i in range(20)]
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    resp = await client.get("/api/search?q=budget&page=1&limit=20")
    data = resp.json()
    assert data["pagination"]["total"] == 100
    assert data["pagination"]["has_next"] is True


# ── Cache ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_served_from_cache(client, mock_db, patch_cache):
    patch_cache["get"].return_value = {
        "query": "budget",
        "results": [],
        "pagination": {"page": 1, "limit": 20, "total": 0, "has_next": False},
    }

    resp = await client.get("/api/search?q=budget")
    assert resp.status_code == 200
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_search_sets_cache_with_shorter_ttl(client, mock_db, patch_cache):
    """Search uses search_cache_ttl_seconds, not the default TTL."""
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    rows_result = MagicMock()
    rows_result.all.return_value = []
    mock_db.execute = AsyncMock(side_effect=[count_result, rows_result])

    from backend.config import settings
    await client.get("/api/search?q=test")
    _, kwargs = patch_cache["set"].call_args
    assert kwargs.get("ttl") == settings.search_cache_ttl_seconds
