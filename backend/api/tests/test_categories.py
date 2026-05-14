"""Tests for GET /api/categories and GET /api/categories/{slug}"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.api.schemas import CATEGORY_LABELS
from backend.api.tests.conftest import make_agenda_item


# ── GET /api/categories ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_categories_returns_all_12(client, mock_db):
    rows_result = MagicMock()
    rows_result.all.return_value = [
        ("budget-finance", 10),
        ("schools-education", 5),
    ]
    mock_db.execute = AsyncMock(return_value=rows_result)

    resp = await client.get("/api/categories")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["categories"]) == 12


@pytest.mark.asyncio
async def test_list_categories_counts_populated(client, mock_db):
    rows_result = MagicMock()
    rows_result.all.return_value = [
        ("budget-finance", 7),
        ("transportation", 3),
    ]
    mock_db.execute = AsyncMock(return_value=rows_result)

    resp = await client.get("/api/categories")
    cats = {c["slug"]: c["item_count"] for c in resp.json()["categories"]}
    assert cats["budget-finance"] == 7
    assert cats["transportation"] == 3
    assert cats["general"] == 0  # not in DB rows → defaults to 0


@pytest.mark.asyncio
async def test_list_categories_has_correct_labels(client, mock_db):
    rows_result = MagicMock()
    rows_result.all.return_value = []
    mock_db.execute = AsyncMock(return_value=rows_result)

    resp = await client.get("/api/categories")
    labels = {c["slug"]: c["label"] for c in resp.json()["categories"]}
    for slug, expected_label in CATEGORY_LABELS.items():
        assert labels[slug] == expected_label


@pytest.mark.asyncio
async def test_list_categories_served_from_cache(client, mock_db, patch_cache):
    patch_cache["get"].return_value = {"categories": [{"slug": "general", "label": "General", "item_count": 1}]}

    resp = await client.get("/api/categories")
    assert resp.status_code == 200
    mock_db.execute.assert_not_called()


# ── GET /api/categories/{slug} ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_category_feed_returns_200(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 2
    items_result = MagicMock()
    items_result.scalars.return_value.all.return_value = [
        make_agenda_item(id=1), make_agenda_item(id=2)
    ]
    mock_db.execute = AsyncMock(side_effect=[count_result, items_result])

    resp = await client.get("/api/categories/budget-finance")
    assert resp.status_code == 200
    data = resp.json()
    assert data["slug"] == "budget-finance"
    assert data["label"] == "Budget & Finance"
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_get_category_feed_404_for_unknown_slug(client, mock_db):
    resp = await client.get("/api/categories/not-a-real-category")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_category_feed_pagination(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 45
    items_result = MagicMock()
    items_result.scalars.return_value.all.return_value = [make_agenda_item(id=i) for i in range(1, 21)]
    mock_db.execute = AsyncMock(side_effect=[count_result, items_result])

    resp = await client.get("/api/categories/schools-education?page=1&limit=20")
    assert resp.status_code == 200
    data = resp.json()
    assert data["pagination"]["total"] == 45
    assert data["pagination"]["has_next"] is True


@pytest.mark.asyncio
async def test_get_category_feed_empty(client, mock_db):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 0
    items_result = MagicMock()
    items_result.scalars.return_value.all.return_value = []
    mock_db.execute = AsyncMock(side_effect=[count_result, items_result])

    resp = await client.get("/api/categories/technology")
    assert resp.status_code == 200
    assert resp.json()["items"] == []
    assert resp.json()["pagination"]["total"] == 0


@pytest.mark.asyncio
async def test_get_category_feed_sets_cache(client, mock_db, patch_cache):
    count_result = MagicMock()
    count_result.scalar_one.return_value = 1
    items_result = MagicMock()
    items_result.scalars.return_value.all.return_value = [make_agenda_item()]
    mock_db.execute = AsyncMock(side_effect=[count_result, items_result])

    await client.get("/api/categories/general")
    patch_cache["set"].assert_called_once()


@pytest.mark.asyncio
async def test_all_12_slugs_return_200(client, mock_db):
    for slug in CATEGORY_LABELS:
        count_result = MagicMock()
        count_result.scalar_one.return_value = 0
        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(side_effect=[count_result, items_result])

        resp = await client.get(f"/api/categories/{slug}")
        assert resp.status_code == 200, f"Slug {slug!r} returned {resp.status_code}"
