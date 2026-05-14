"""Tests for backend/pipeline/deduplicator.py"""

import hashlib
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.pipeline.deduplicator import (
    filter_new_documents,
    is_already_processed,
    upsert_seen_document,
)
from backend.pipeline.scrapers.base import DocumentInfo


def _make_doc(url: str = "https://example.gov/agenda.pdf") -> DocumentInfo:
    return DocumentInfo(
        url=url,
        pdf_url=url,
        title="Test Agenda",
        meeting_date=date(2024, 5, 14),
        board_type="lcps",
    )


def _mock_session(record=None):
    session = AsyncMock()
    result = MagicMock()
    result.scalar_one_or_none.return_value = record
    session.execute = AsyncMock(return_value=result)
    return session


# ── is_already_processed ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_is_already_processed_returns_false_when_not_found():
    session = _mock_session(record=None)
    result = await is_already_processed(session, "https://example.gov/new.pdf", "abc123")
    assert result is False


@pytest.mark.asyncio
async def test_is_already_processed_returns_true_when_completed_and_hash_matches():
    record = MagicMock()
    record.status = "completed"
    record.sha256 = hashlib.sha256(b"content").hexdigest()

    session = _mock_session(record=record)
    result = await is_already_processed(
        session, "https://example.gov/done.pdf", record.sha256
    )
    assert result is True


@pytest.mark.asyncio
async def test_is_already_processed_returns_false_when_status_not_completed():
    record = MagicMock()
    record.status = "failed"
    record.sha256 = "somehash"

    session = _mock_session(record=record)
    result = await is_already_processed(session, "https://example.gov/failed.pdf", "somehash")
    assert result is False


@pytest.mark.asyncio
async def test_is_already_processed_returns_false_when_hash_differs():
    record = MagicMock()
    record.status = "completed"
    record.sha256 = "oldhash"

    session = _mock_session(record=record)
    result = await is_already_processed(session, "https://example.gov/updated.pdf", "newhash")
    assert result is False


# ── upsert_seen_document ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_seen_document_creates_new_record():
    session = _mock_session(record=None)
    content = b"pdf content"
    expected_hash = hashlib.sha256(content).hexdigest()

    record = await upsert_seen_document(session, "https://example.gov/new.pdf", content)

    assert record.url == "https://example.gov/new.pdf"
    assert record.sha256 == expected_hash
    assert record.status == "pending"
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_upsert_seen_document_updates_existing_record():
    existing = MagicMock()
    existing.url = "https://example.gov/existing.pdf"
    existing.sha256 = "oldhash"
    existing.status = "failed"

    session = _mock_session(record=existing)
    content = b"new pdf content"
    expected_hash = hashlib.sha256(content).hexdigest()

    record = await upsert_seen_document(
        session, "https://example.gov/existing.pdf", content, status="processing"
    )

    assert record.sha256 == expected_hash
    assert record.status == "processing"
    session.add.assert_not_called()


# ── filter_new_documents ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_filter_new_documents_returns_all_when_none_exist():
    docs = [_make_doc(f"https://example.gov/{i}.pdf") for i in range(3)]

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.__iter__ = MagicMock(return_value=iter([]))
    session.execute = AsyncMock(return_value=result_mock)

    new_docs = await filter_new_documents(session, docs)
    assert len(new_docs) == 3


@pytest.mark.asyncio
async def test_filter_new_documents_skips_completed():
    url_done = "https://example.gov/done.pdf"
    url_new = "https://example.gov/new.pdf"
    docs = [_make_doc(url_done), _make_doc(url_new)]

    row_done = MagicMock()
    row_done.url = url_done
    row_done.sha256 = "somehash"
    row_done.status = "completed"

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.__iter__ = MagicMock(return_value=iter([row_done]))
    session.execute = AsyncMock(return_value=result_mock)

    new_docs = await filter_new_documents(session, docs)
    assert len(new_docs) == 1
    assert new_docs[0].pdf_url == url_new


@pytest.mark.asyncio
async def test_filter_new_documents_includes_failed_for_retry():
    url_failed = "https://example.gov/failed.pdf"
    docs = [_make_doc(url_failed)]

    row_failed = MagicMock()
    row_failed.url = url_failed
    row_failed.sha256 = "somehash"
    row_failed.status = "failed"

    session = AsyncMock()
    result_mock = MagicMock()
    result_mock.__iter__ = MagicMock(return_value=iter([row_failed]))
    session.execute = AsyncMock(return_value=result_mock)

    new_docs = await filter_new_documents(session, docs)
    assert len(new_docs) == 1


@pytest.mark.asyncio
async def test_filter_new_documents_empty_input():
    session = AsyncMock()
    result = await filter_new_documents(session, [])
    assert result == []
    session.execute.assert_not_called()
