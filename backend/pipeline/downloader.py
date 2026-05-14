"""
PDF downloader for government document URLs.
Downloads with browser-like headers, validates MIME type, saves to temp dir.
"""

import hashlib
import logging
import tempfile
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/pdf,*/*",
}

_TIMEOUT = httpx.Timeout(connect=10, read=60, write=30, pool=5)
_MAX_RETRIES = 3


class DownloadError(Exception):
    pass


def _temp_path(url: str) -> Path:
    name = hashlib.sha256(url.encode()).hexdigest()[:16]
    return Path(tempfile.gettempdir()) / f"{name}.pdf"


async def download_pdf(url: str) -> Path:
    """Download a PDF from *url* and return the local temp path.

    Retries up to _MAX_RETRIES times with exponential backoff.
    Raises DownloadError on failure or non-PDF response.
    """
    import asyncio

    dest = _temp_path(url)
    if dest.exists():
        logger.debug("Cache hit for %s → %s", url, dest)
        return dest

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            async with httpx.AsyncClient(
                headers=_HEADERS, timeout=_TIMEOUT, follow_redirects=True
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "application/pdf" not in content_type and not url.lower().endswith(".pdf"):
                raise DownloadError(
                    f"Expected application/pdf, got '{content_type}' for {url}"
                )

            dest.write_bytes(resp.content)
            logger.info("Downloaded %s → %s (%d bytes)", url, dest, len(resp.content))
            return dest

        except DownloadError:
            raise
        except (httpx.HTTPError, OSError) as exc:
            last_exc = exc
            if attempt < _MAX_RETRIES - 1:
                wait = 2 ** attempt
                logger.warning("Download attempt %d failed (%s), retrying in %ds", attempt + 1, exc, wait)
                await asyncio.sleep(wait)

    raise DownloadError(f"Failed to download {url} after {_MAX_RETRIES} attempts: {last_exc}") from last_exc
