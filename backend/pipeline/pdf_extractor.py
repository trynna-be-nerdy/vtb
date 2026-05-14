"""
PDF text extraction using pdfplumber.
Extracts page-by-page text, filters repeated headers/footers.
"""

import logging
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

logger = logging.getLogger(__name__)


class PdfExtractionError(Exception):
    pass


@dataclass
class PageText:
    page_num: int   # 1-based
    text: str
    char_count: int


def extract_text(pdf_path: Path) -> list[PageText]:
    """Extract text from each page of *pdf_path*.

    Returns a list of PageText in page order. Empty/image-only pages are
    included with empty text so that page numbering stays accurate.
    Raises PdfExtractionError for encrypted or unreadable PDFs.
    """
    if not pdf_path.exists():
        raise PdfExtractionError(f"File not found: {pdf_path}")

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.metadata.get("Encrypt"):
                raise PdfExtractionError(f"PDF is encrypted: {pdf_path}")

            raw_pages: list[tuple[int, str]] = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                raw_pages.append((page.page_number, text))

        boilerplate = _detect_boilerplate([t for _, t in raw_pages])
        pages: list[PageText] = []
        for page_num, text in raw_pages:
            cleaned = _strip_boilerplate(text, boilerplate)
            pages.append(PageText(page_num=page_num, text=cleaned, char_count=len(cleaned)))

        logger.info("Extracted %d pages from %s", len(pages), pdf_path)
        return pages

    except PdfExtractionError:
        raise
    except Exception as exc:
        raise PdfExtractionError(f"Failed to extract {pdf_path}: {exc}") from exc


def _detect_boilerplate(page_texts: list[str], threshold: float = 0.6) -> set[str]:
    """Return lines that appear on more than *threshold* fraction of pages."""
    if len(page_texts) < 3:
        return set()

    line_counts: Counter[str] = Counter()
    for text in page_texts:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                line_counts[stripped] += 1

    cutoff = max(2, int(len(page_texts) * threshold))
    return {line for line, count in line_counts.items() if count >= cutoff}


def _strip_boilerplate(text: str, boilerplate: set[str]) -> str:
    if not boilerplate:
        return text
    lines = [l for l in text.splitlines() if l.strip() not in boilerplate]
    return "\n".join(lines)
