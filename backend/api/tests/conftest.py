"""
Shared fixtures for API endpoint tests.

Strategy:
- Override get_db FastAPI dependency with a mock async session.
- Patch cache_get/cache_set at the route-module level (routes use 'from X import Y'
  so the source-module patch doesn't reach the local names they hold).
- Use httpx.AsyncClient with ASGITransport for full ASGI coverage.
"""

from datetime import date, datetime, timezone
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.api.main import app
from backend.api.deps import get_db

_ROUTE_MODULES = [
    "backend.api.routes.meetings",
    "backend.api.routes.categories",
    "backend.api.routes.search",
    "backend.api.routes.health",
]


# ── DB session mock factory ──────────────────────────────────────────────────

def make_db_session() -> AsyncMock:
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one.return_value = 0
    result.scalar_one_or_none.return_value = None
    result.scalars.return_value.all.return_value = []
    result.all.return_value = []
    session.execute = AsyncMock(return_value=result)
    return session


@pytest.fixture
def mock_db():
    return make_db_session()


@pytest.fixture(autouse=True)
def patch_cache():
    """Patch cache_get/cache_set in every route module that imports them.

    Default behaviour: cache always misses (get returns None), set is a no-op.
    Tests that need a cache hit can do: patch_cache["get"].return_value = {...}
    """
    mock_get = AsyncMock(return_value=None)
    mock_set = AsyncMock()

    patches = []
    for mod in _ROUTE_MODULES:
        patches.append(patch(f"{mod}.cache_get", mock_get))
        patches.append(patch(f"{mod}.cache_set", mock_set))

    for p in patches:
        p.start()

    yield {"get": mock_get, "set": mock_set}

    for p in patches:
        p.stop()


@pytest_asyncio.fixture
async def client(mock_db) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_db] = lambda: mock_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Sample data builders ─────────────────────────────────────────────────────

def make_meeting(
    id: int = 1,
    title: str = "Regular Board Meeting",
    board_slug: str = "lcps",
    meeting_date: date = date(2024, 5, 14),
    processing_status: str = "completed",
) -> MagicMock:
    m = MagicMock()
    m.id = id
    m.title = title
    m.board_slug = board_slug
    m.meeting_date = meeting_date
    m.meeting_overview = "Overview of the meeting."
    m.top_decisions = ["Approved budget", "Hired superintendent"]
    m.fiscal_total = "$1.2M"
    m.total_items = 5
    m.fiscal_items = 2
    m.processing_status = processing_status
    m.source_url = "https://example.gov/meeting"
    m.source_pdf_url = "https://example.gov/agenda.pdf"
    m.next_meeting_notes = "Next meeting June 11"
    m.updated_at = datetime.now(timezone.utc)
    m.agenda_items = []
    m.supporting_documents = []
    return m


def make_agenda_item(
    id: int = 1,
    meeting_id: int = 1,
    primary_category: str = "budget-finance",
) -> MagicMock:
    item = MagicMock()
    item.id = id
    item.meeting_id = meeting_id
    item.title = "Budget Amendment FY2024"
    item.summary = "The board approved a $500K budget amendment."
    item.primary_category = primary_category
    item.secondary_tags = ["schools", "capital"]
    item.urgency = "notable"
    item.fiscal_impact = True
    item.affects_schools = ["Briar Woods High School"]
    item.source_pdf_url = "https://example.gov/item1.pdf"
    item.page_range = "pp. 5-8"
    item.created_at = datetime.now(timezone.utc)
    item.decisions = ["Approved 5-2"]
    item.action_items = ["CFO to report back in 30 days"]
    item.key_figures = {"amounts": ["$500,000"], "vote_tallies": ["5-2"]}
    return item
