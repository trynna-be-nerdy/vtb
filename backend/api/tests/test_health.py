"""Tests for GET /api/health"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest


def _make_pipeline_run(status: str = "completed") -> MagicMock:
    run = MagicMock()
    run.started_at = datetime(2024, 5, 14, 10, 0, 0, tzinfo=timezone.utc)
    run.status = status
    return run


# ── GET /api/health ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_returns_200(client, mock_db):
    run_result = MagicMock()
    run_result.scalar_one_or_none.return_value = _make_pipeline_run()
    count_items = MagicMock()
    count_items.scalar_one.return_value = 42
    count_queue = MagicMock()
    count_queue.scalar_one.return_value = 3

    mock_db.execute = AsyncMock(side_effect=[run_result, count_items, count_queue])

    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_includes_all_fields(client, mock_db):
    run_result = MagicMock()
    run_result.scalar_one_or_none.return_value = _make_pipeline_run("completed")
    count_items = MagicMock()
    count_items.scalar_one.return_value = 15
    count_queue = MagicMock()
    count_queue.scalar_one.return_value = 2

    mock_db.execute = AsyncMock(side_effect=[run_result, count_items, count_queue])

    resp = await client.get("/api/health")
    data = resp.json()
    assert "status" in data
    assert "last_pipeline_run" in data
    assert "last_pipeline_status" in data
    assert "items_this_month" in data
    assert "queue_depth" in data


@pytest.mark.asyncio
async def test_health_with_no_pipeline_runs(client, mock_db):
    run_result = MagicMock()
    run_result.scalar_one_or_none.return_value = None
    count_items = MagicMock()
    count_items.scalar_one.return_value = 0
    count_queue = MagicMock()
    count_queue.scalar_one.return_value = 0

    mock_db.execute = AsyncMock(side_effect=[run_result, count_items, count_queue])

    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["last_pipeline_run"] is None
    assert data["last_pipeline_status"] is None


@pytest.mark.asyncio
async def test_health_reports_correct_counts(client, mock_db):
    run_result = MagicMock()
    run_result.scalar_one_or_none.return_value = _make_pipeline_run()
    count_items = MagicMock()
    count_items.scalar_one.return_value = 99
    count_queue = MagicMock()
    count_queue.scalar_one.return_value = 7

    mock_db.execute = AsyncMock(side_effect=[run_result, count_items, count_queue])

    resp = await client.get("/api/health")
    data = resp.json()
    assert data["items_this_month"] == 99
    assert data["queue_depth"] == 7


@pytest.mark.asyncio
async def test_health_served_from_cache(client, mock_db, patch_cache):
    patch_cache["get"].return_value = {
        "status": "ok",
        "last_pipeline_run": None,
        "last_pipeline_status": None,
        "items_this_month": 0,
        "queue_depth": 0,
    }

    resp = await client.get("/api/health")
    assert resp.status_code == 200
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_health_uses_short_cache_ttl(client, mock_db, patch_cache):
    """Health uses health_cache_ttl_seconds (30s), not the default 15min."""
    run_result = MagicMock()
    run_result.scalar_one_or_none.return_value = None
    count_items = MagicMock()
    count_items.scalar_one.return_value = 0
    count_queue = MagicMock()
    count_queue.scalar_one.return_value = 0

    mock_db.execute = AsyncMock(side_effect=[run_result, count_items, count_queue])

    from backend.config import settings
    await client.get("/api/health")
    _, kwargs = patch_cache["set"].call_args
    assert kwargs.get("ttl") == settings.health_cache_ttl_seconds
