"""Splits raw PDF text into agenda item chunks.

Strategy: split on known agenda item headers, then cap each chunk at
PDF_CHUNK_MAX_CHARS to avoid overflowing Gemma 4's context.
"""
import logging
import re

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Patterns that indicate the start of a new agenda item
ITEM_HEADER_PATTERN = re.compile(
    r"""
    (?:^|\n)                          # line start
    (?:
        AGENDA\s+ITEM\s*[\d\.]+       # "AGENDA ITEM 3" or "AGENDA ITEM 3.1"
      | ITEM\s+[\d\.]+\b              # "ITEM 4" or "ITEM 4.2"
      | PUBLIC\s+HEARING\b            # "PUBLIC HEARING"
      | ACTION\s+ITEM\s*[\d\.]+       # "ACTION ITEM 2"
      | CONSENT\s+AGENDA\b            # "CONSENT AGENDA"
      | INFORMATION\s+ITEM\s*[\d\.]+ # "INFORMATION ITEM 1"
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)


def split_into_chunks(pages: list[str]) -> list[str]:
    """Split page text into agenda-item-level chunks.

    1. Concatenate all pages into one document string.
    2. Split on agenda item header patterns.
    3. Cap each chunk at PDF_CHUNK_MAX_CHARS.
    4. Drop chunks that are too short to be meaningful (< 100 chars).
    """
    full_text = "\n\n".join(pages)
    raw_chunks = ITEM_HEADER_PATTERN.split(full_text)

    chunks: list[str] = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if len(chunk) < 100:
            continue  # Too short — likely a header artifact
        # Cap length
        if len(chunk) > settings.pdf_chunk_max_chars:
            # Split into sub-chunks at paragraph boundaries
            paragraphs = chunk.split("\n\n")
            current = ""
            for para in paragraphs:
                if len(current) + len(para) + 2 > settings.pdf_chunk_max_chars:
                    if current:
                        chunks.append(current.strip())
                    current = para
                else:
                    current = f"{current}\n\n{para}" if current else para
            if current.strip():
                chunks.append(current.strip())
        else:
            chunks.append(chunk)

    logger.info("Produced %d chunks from %d pages", len(chunks), len(pages))
    return chunks
