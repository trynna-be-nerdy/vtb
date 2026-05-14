"""Integration tests for backend/pipeline/__init__.py (process_pdf)."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.pipeline import ProcessingResult, process_pdf
from backend.pipeline.chunker import Chunk
from backend.pipeline.downloader import DownloadError
from backend.pipeline.pdf_extractor import PageText, PdfExtractionError


def _mock_pages() -> list[PageText]:
    return [
        PageText(page_num=1, text="Item 1 Budget Discussion\nThe board reviewed the budget.", char_count=55),
        PageText(page_num=2, text="Item 2 School Safety\nSafety measures were approved.", char_count=54),
    ]


@pytest.mark.asyncio
async def test_process_pdf_returns_processing_result():
    url = "https://example.gov/meeting.pdf"
    fake_path = Path(tempfile.gettempdir()) / "fake_test.pdf"
    fake_path.write_bytes(b"fake pdf")

    with patch("backend.pipeline.download_pdf", new_callable=AsyncMock, return_value=fake_path):
        with patch("backend.pipeline.extract_text", return_value=_mock_pages()):
            result = await process_pdf(url)

    assert isinstance(result, ProcessingResult)
    assert result.source_url == url
    assert result.page_count == 2
    assert len(result.chunks) > 0
    assert result.url_sha256  # non-empty hash
    assert not fake_path.exists()  # cleaned up


@pytest.mark.asyncio
async def test_process_pdf_cleans_up_on_extraction_error():
    url = "https://example.gov/bad.pdf"
    fake_path = Path(tempfile.gettempdir()) / "fake_bad.pdf"
    fake_path.write_bytes(b"fake pdf")

    with patch("backend.pipeline.download_pdf", new_callable=AsyncMock, return_value=fake_path):
        with patch("backend.pipeline.extract_text", side_effect=PdfExtractionError("bad pdf")):
            with pytest.raises(PdfExtractionError):
                await process_pdf(url)

    assert not fake_path.exists()


@pytest.mark.asyncio
async def test_process_pdf_propagates_download_error():
    url = "https://example.gov/missing.pdf"

    with patch(
        "backend.pipeline.download_pdf",
        new_callable=AsyncMock,
        side_effect=DownloadError("network failure"),
    ):
        with pytest.raises(DownloadError, match="network failure"):
            await process_pdf(url)


@pytest.mark.asyncio
async def test_process_pdf_url_sha256_is_correct():
    import hashlib

    url = "https://example.gov/agenda.pdf"
    fake_path = Path(tempfile.gettempdir()) / "fake_sha.pdf"
    fake_path.write_bytes(b"fake")

    with patch("backend.pipeline.download_pdf", new_callable=AsyncMock, return_value=fake_path):
        with patch("backend.pipeline.extract_text", return_value=_mock_pages()):
            result = await process_pdf(url)

    expected = hashlib.sha256(url.encode()).hexdigest()
    assert result.url_sha256 == expected


@pytest.mark.asyncio
async def test_process_pdf_total_chars_sums_pages():
    url = "https://example.gov/chars.pdf"
    fake_path = Path(tempfile.gettempdir()) / "fake_chars.pdf"
    fake_path.write_bytes(b"fake")

    pages = _mock_pages()
    expected_total = sum(p.char_count for p in pages)

    with patch("backend.pipeline.download_pdf", new_callable=AsyncMock, return_value=fake_path):
        with patch("backend.pipeline.extract_text", return_value=pages):
            result = await process_pdf(url)

    assert result.total_chars == expected_total
