"""Tests for backend/pipeline/downloader.py"""

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from backend.pipeline.downloader import DownloadError, _temp_path, download_pdf


def test_temp_path_is_deterministic():
    url = "https://example.gov/meeting.pdf"
    p1 = _temp_path(url)
    p2 = _temp_path(url)
    assert p1 == p2
    assert p1.suffix == ".pdf"
    expected_name = hashlib.sha256(url.encode()).hexdigest()[:16]
    assert p1.name == f"{expected_name}.pdf"


@pytest.mark.asyncio
async def test_download_success():
    fake_pdf = b"%PDF-1.4 fake content"
    url = "https://example.gov/test.pdf"

    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/pdf"}
    mock_response.content = fake_pdf
    mock_response.raise_for_status = MagicMock()

    with patch("backend.pipeline.downloader._temp_path") as mock_path:
        dest = Path(tempfile.gettempdir()) / "test_dl_success.pdf"
        dest.unlink(missing_ok=True)
        mock_path.return_value = dest

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await download_pdf(url)
            assert result == dest
            assert dest.read_bytes() == fake_pdf
        dest.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_download_rejects_non_pdf_content_type():
    url = "https://example.gov/notapdf.html"

    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/html"}
    mock_response.content = b"<html></html>"
    mock_response.raise_for_status = MagicMock()

    with patch("backend.pipeline.downloader._temp_path") as mock_path:
        dest = Path(tempfile.gettempdir()) / "test_dl_mime.pdf"
        dest.unlink(missing_ok=True)
        mock_path.return_value = dest

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            with pytest.raises(DownloadError, match="application/pdf"):
                await download_pdf(url)


@pytest.mark.asyncio
async def test_download_allows_pdf_url_without_content_type():
    """A URL ending in .pdf with generic content-type should still succeed."""
    fake_pdf = b"%PDF-1.4 content"
    url = "https://example.gov/agenda.pdf"

    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/octet-stream"}
    mock_response.content = fake_pdf
    mock_response.raise_for_status = MagicMock()

    with patch("backend.pipeline.downloader._temp_path") as mock_path:
        dest = Path(tempfile.gettempdir()) / "test_dl_octet.pdf"
        dest.unlink(missing_ok=True)
        mock_path.return_value = dest

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(return_value=mock_response)
            mock_client_cls.return_value = mock_client

            result = await download_pdf(url)
            assert result == dest
        dest.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_download_retries_on_http_error():
    url = "https://example.gov/flaky.pdf"

    call_count = 0

    async def flaky_get(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise httpx.ConnectError("connection refused")
        resp = MagicMock()
        resp.headers = {"content-type": "application/pdf"}
        resp.content = b"%PDF fake"
        resp.raise_for_status = MagicMock()
        return resp

    with patch("backend.pipeline.downloader._temp_path") as mock_path:
        dest = Path(tempfile.gettempdir()) / "test_dl_retry.pdf"
        dest.unlink(missing_ok=True)
        mock_path.return_value = dest

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = flaky_get
            mock_client_cls.return_value = mock_client

            with patch("asyncio.sleep", new_callable=AsyncMock):
                result = await download_pdf(url)
                assert result == dest
                assert call_count == 3
        dest.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_download_raises_after_max_retries():
    url = "https://example.gov/always_fail.pdf"

    with patch("backend.pipeline.downloader._temp_path") as mock_path:
        dest = Path(tempfile.gettempdir()) / "test_dl_maxretry.pdf"
        dest.unlink(missing_ok=True)
        mock_path.return_value = dest

        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))
            mock_client_cls.return_value = mock_client

            with patch("asyncio.sleep", new_callable=AsyncMock):
                with pytest.raises(DownloadError, match="after 3 attempts"):
                    await download_pdf(url)


@pytest.mark.asyncio
async def test_download_returns_cached_file(tmp_path):
    url = "https://example.gov/cached.pdf"
    dest = tmp_path / "cached.pdf"
    dest.write_bytes(b"%PDF already here")

    with patch("backend.pipeline.downloader._temp_path", return_value=dest):
        result = await download_pdf(url)
        assert result == dest
