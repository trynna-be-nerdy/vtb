"""
Abstract base scraper and shared data types for the VtB pipeline.
"""

import asyncio
import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

_RATE_LIMIT_SECONDS = 4.0  # minimum delay between outbound requests

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_JSON_HEADERS = {
    **_BROWSER_HEADERS,
    "Accept": "application/json, text/plain, */*",
}


@dataclass
class DocumentInfo:
    url: str              # landing page URL
    pdf_url: str          # direct PDF download link
    title: str
    meeting_date: date
    board_type: str       # lcps | supervisors | planning | advisory
    sha256_hash: str = field(default="")  # populated after download

    def compute_hash(self, content: bytes) -> None:
        self.sha256_hash = hashlib.sha256(content).hexdigest()


class BaseScraper(ABC):
    """Common HTTP client + rate-limiting logic shared by all scrapers."""

    def __init__(self) -> None:
        self._last_request_time: float = 0.0
        self._timeout = httpx.Timeout(connect=10, read=30, write=10, pool=5)

    async def _get(self, url: str, *, json: bool = False) -> httpx.Response:
        """Rate-limited GET. Never issues parallel requests from the same instance."""
        now = asyncio.get_event_loop().time()
        wait = _RATE_LIMIT_SECONDS - (now - self._last_request_time)
        if wait > 0:
            await asyncio.sleep(wait)

        headers = _JSON_HEADERS if json else _BROWSER_HEADERS
        async with httpx.AsyncClient(
            headers=headers, timeout=self._timeout, follow_redirects=True
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

        self._last_request_time = asyncio.get_event_loop().time()
        logger.debug("GET %s → %d", url, resp.status_code)
        return resp

    async def fetch_document(self, url: str) -> bytes:
        """Download raw bytes from *url* (rate-limited)."""
        resp = await self._get(url)
        return resp.content

    @abstractmethod
    async def discover_documents(self) -> list[DocumentInfo]:
        """Return a list of DocumentInfo for newly discovered meeting documents."""
