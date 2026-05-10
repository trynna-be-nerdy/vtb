"""PDF downloader + pdfplumber text extractor."""
import hashlib
import logging
import tempfile
from pathlib import Path

import httpx
import pdfplumber

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}


def download_pdf(url: str) -> tuple[bytes, str]:
    """Download a PDF and return (content_bytes, sha256_hex).

    Raises httpx.HTTPError on network failure.
    Raises ValueError if the response is not a PDF.
    """
    with httpx.Client(timeout=60) as client:
        response = client.get(url, headers=BROWSER_HEADERS, follow_redirects=True)
        response.raise_for_status()

    content_type = response.headers.get("content-type", "")
    if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
        raise ValueError(f"URL did not return a PDF (content-type: {content_type})")

    content = response.content
    sha256 = hashlib.sha256(content).hexdigest()
    logger.info("Downloaded %d bytes from %s (sha256: %s...)", len(content), url, sha256[:12])
    return content, sha256


def extract_text_from_bytes(pdf_bytes: bytes) -> list[str]:
    """Extract text page-by-page from PDF bytes using pdfplumber.

    Returns a list of strings, one per page.
    """
    pages: list[str] = []
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = Path(tmp.name)

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                pages.append(text.strip())
        logger.info("Extracted text from %d pages", len(pages))
    finally:
        tmp_path.unlink(missing_ok=True)

    return pages
