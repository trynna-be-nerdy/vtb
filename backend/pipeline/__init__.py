"""
PDF processing pipeline: download → extract → chunk.
Entry point: process_pdf(url) -> ProcessingResult
"""

import hashlib
import logging
from dataclasses import dataclass, field

from .chunker import Chunk, chunk_text
from .downloader import DownloadError, download_pdf
from .pdf_extractor import PdfExtractionError, extract_text

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    chunks: list[Chunk]
    source_url: str
    page_count: int
    total_chars: int
    url_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        self.url_sha256 = hashlib.sha256(self.source_url.encode()).hexdigest()


async def process_pdf(url: str) -> ProcessingResult:
    """Download, extract, and chunk a PDF from *url*.

    Cleans up the temp file after processing.
    Raises DownloadError or PdfExtractionError on failure.
    """
    pdf_path = await download_pdf(url)
    try:
        pages = extract_text(pdf_path)
        chunks = chunk_text(pages)
        total_chars = sum(p.char_count for p in pages)
        logger.info(
            "Processed %s: %d pages, %d chunks, %d chars",
            url, len(pages), len(chunks), total_chars,
        )
        return ProcessingResult(
            chunks=chunks,
            source_url=url,
            page_count=len(pages),
            total_chars=total_chars,
        )
    finally:
        if pdf_path.exists():
            pdf_path.unlink(missing_ok=True)
            logger.debug("Cleaned up temp file %s", pdf_path)
