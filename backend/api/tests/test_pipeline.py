"""Tests for POST /api/pipeline/trigger"""

from unittest.mock import AsyncMock, patch

import pytest

from backend.config import settings


# ── POST /api/pipeline/trigger ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_trigger_pipeline_with_valid_key(client, mock_db):
    with patch("backend.cache.client.publish_update", new_callable=AsyncMock):
        resp = await client.post(
            "/api/pipeline/trigger",
            headers={"x-api-key": settings.pipeline_api_key},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["triggered"] is True
    assert "message" in data


@pytest.mark.asyncio
async def test_trigger_pipeline_rejects_missing_key(client, mock_db):
    resp = await client.post("/api/pipeline/trigger")
    assert resp.status_code == 422  # missing required header


@pytest.mark.asyncio
async def test_trigger_pipeline_rejects_wrong_key(client, mock_db):
    resp = await client.post(
        "/api/pipeline/trigger",
        headers={"x-api-key": "wrong-key"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Invalid API key"


@pytest.mark.asyncio
async def test_trigger_pipeline_publishes_redis_event(client, mock_db):
    with patch("backend.cache.client.publish_update", new_callable=AsyncMock) as mock_publish:
        await client.post(
            "/api/pipeline/trigger",
            headers={"x-api-key": settings.pipeline_api_key},
        )
        # publish_update is called as a background task — give event loop a tick
        import asyncio
        await asyncio.sleep(0)
        mock_publish.assert_called_once_with({"event": "pipeline_triggered"})


@pytest.mark.asyncio
async def test_trigger_pipeline_response_message_is_helpful(client, mock_db):
    with patch("backend.cache.client.publish_update", new_callable=AsyncMock):
        resp = await client.post(
            "/api/pipeline/trigger",
            headers={"x-api-key": settings.pipeline_api_key},
        )
    assert "/api/health" in resp.json()["message"]
