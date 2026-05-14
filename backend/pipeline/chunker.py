"""
Agenda item chunker.
Splits extracted page text into Chunk objects aligned to agenda item headers.
"""

import re
from dataclasses import dataclass
from typing import Optional

from .pdf_extractor import PageText

MAX_CHUNK_CHARS = 2_000
CONTEXT_OVERLAP = 200

_HEADER_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?:Item|ITEM)\s*\d+\.?[A-Z]?", re.IGNORECASE),
    re.compile(r"(?:Action|ACTION)\s+(?:Item|ITEM)", re.IGNORECASE),
    re.compile(r"(?:Consent|CONSENT)\s+(?:Agenda|AGENDA)", re.IGNORECASE),
    re.compile(r"(?:PUBLIC|CITIZEN)\s+(?:HEARING|COMMENT)", re.IGNORECASE),
]


@dataclass
class Chunk:
    text: str
    page_start: int
    page_end: int
    detected_header: Optional[str]
    char_count: int


def chunk_text(pages: list[PageText]) -> list[Chunk]:
    """Split *pages* into agenda-item-aligned chunks of at most MAX_CHUNK_CHARS."""
    if not pages:
        return []

    # Annotate each line with its source page number
    lines: list[tuple[str, int]] = []
    for page in pages:
        for line in page.text.splitlines():
            lines.append((line, page.page_num))

    segments = _split_on_headers(lines)
    chunks: list[Chunk] = []
    for header, seg_lines in segments:
        seg_text = "\n".join(l for l, _ in seg_lines)
        seg_pages = [p for _, p in seg_lines if p is not None]
        page_start = seg_pages[0] if seg_pages else pages[0].page_num
        page_end = seg_pages[-1] if seg_pages else pages[-1].page_num

        if len(seg_text) <= MAX_CHUNK_CHARS:
            chunks.append(Chunk(
                text=seg_text,
                page_start=page_start,
                page_end=page_end,
                detected_header=header,
                char_count=len(seg_text),
            ))
        else:
            chunks.extend(_split_oversized(seg_text, page_start, page_end, header))

    return chunks


def _detect_header(line: str) -> Optional[str]:
    stripped = line.strip()
    for pattern in _HEADER_PATTERNS:
        if pattern.search(stripped):
            return stripped
    return None


def _split_on_headers(
    lines: list[tuple[str, int]],
) -> list[tuple[Optional[str], list[tuple[str, int]]]]:
    """Group lines into (header, lines) segments split at each header match."""
    segments: list[tuple[Optional[str], list[tuple[str, int]]]] = []
    current_header: Optional[str] = None
    current_lines: list[tuple[str, int]] = []

    for line, page in lines:
        header = _detect_header(line)
        if header is not None:
            if current_lines:
                segments.append((current_header, current_lines))
            # Carry CONTEXT_OVERLAP chars of previous segment as context prefix
            context = _trailing_context(current_lines)
            current_header = header
            current_lines = context + [(line, page)]
        else:
            current_lines.append((line, page))

    if current_lines:
        segments.append((current_header, current_lines))

    return segments


def _trailing_context(lines: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """Return the last ~CONTEXT_OVERLAP chars worth of lines."""
    result: list[tuple[str, int]] = []
    total = 0
    for line, page in reversed(lines):
        total += len(line) + 1
        result.insert(0, (line, page))
        if total >= CONTEXT_OVERLAP:
            break
    return result


def _split_oversized(
    text: str,
    page_start: int,
    page_end: int,
    header: Optional[str],
) -> list[Chunk]:
    """Hard-split *text* into MAX_CHUNK_CHARS pieces, preserving whole lines."""
    pieces: list[Chunk] = []
    current = ""
    is_first = True

    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > MAX_CHUNK_CHARS and current:
            pieces.append(Chunk(
                text=current.rstrip(),
                page_start=page_start,
                page_end=page_end,
                detected_header=header if is_first else None,
                char_count=len(current.rstrip()),
            ))
            current = ""
            is_first = False
        current += line

    if current.strip():
        pieces.append(Chunk(
            text=current.rstrip(),
            page_start=page_start,
            page_end=page_end,
            detected_header=header if is_first else None,
            char_count=len(current.rstrip()),
        ))

    return pieces
