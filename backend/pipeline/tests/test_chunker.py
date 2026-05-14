"""Tests for backend/pipeline/chunker.py"""

import pytest

from backend.pipeline.chunker import (
    MAX_CHUNK_CHARS,
    Chunk,
    _detect_header,
    chunk_text,
)
from backend.pipeline.pdf_extractor import PageText


def make_pages(texts: list[str]) -> list[PageText]:
    return [PageText(page_num=i + 1, text=t, char_count=len(t)) for i, t in enumerate(texts)]


# --- header detection ---

@pytest.mark.parametrize("line,expected", [
    ("Item 5.A - School Budget", "Item 5.A - School Budget"),
    ("ITEM 12 REZONING REQUEST", "ITEM 12 REZONING REQUEST"),
    ("Action Item: Approve contract", "Action Item: Approve contract"),
    ("ACTION ITEM", "ACTION ITEM"),
    ("Consent Agenda", "Consent Agenda"),
    ("CONSENT AGENDA", "CONSENT AGENDA"),
    ("PUBLIC HEARING on zoning", "PUBLIC HEARING on zoning"),
    ("CITIZEN COMMENT period", "CITIZEN COMMENT period"),
    ("Regular paragraph text", None),
    ("The committee discussed items", None),
])
def test_detect_header(line, expected):
    result = _detect_header(line)
    if expected is None:
        assert result is None
    else:
        assert result == expected


# --- chunk_text ---

def test_chunk_text_empty_pages():
    assert chunk_text([]) == []


def test_chunk_text_single_page_no_headers():
    pages = make_pages(["Some general meeting text\nwith multiple lines\nbut no agenda headers"])
    chunks = chunk_text(pages)
    assert len(chunks) == 1
    assert chunks[0].detected_header is None
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1


def test_chunk_text_splits_on_item_header():
    text = (
        "Preamble text here\n"
        "Item 1 - First agenda item\n"
        "Details about the first item\n"
        "Item 2 - Second agenda item\n"
        "Details about the second item"
    )
    pages = make_pages([text])
    chunks = chunk_text(pages)
    headers = [c.detected_header for c in chunks if c.detected_header]
    assert any("Item 1" in h for h in headers)
    assert any("Item 2" in h for h in headers)


def test_chunk_text_all_chunks_under_max_size():
    # Create a page with a header followed by a very long body
    long_body = "word " * 500  # ~2500 chars
    text = f"Item 3 Budget Discussion\n{long_body}"
    pages = make_pages([text])
    chunks = chunk_text(pages)
    for chunk in chunks:
        assert chunk.char_count <= MAX_CHUNK_CHARS, (
            f"Chunk exceeds {MAX_CHUNK_CHARS} chars: {chunk.char_count}"
        )


def test_chunk_text_page_range_spans_multiple_pages():
    pages = make_pages([
        "Item 5 School Construction\nDetails on page one",
        "Continued details on page two\nmore content here",
        "Item 6 Budget Approval\nFinal page content",
    ])
    chunks = chunk_text(pages)
    # Find chunk for Item 5 which spans pages 1-2
    item5_chunks = [c for c in chunks if c.detected_header and "Item 5" in c.detected_header]
    assert item5_chunks, "Should find at least one chunk for Item 5"
    assert item5_chunks[0].page_start == 1


def test_chunk_text_char_count_matches_text():
    pages = make_pages(["Item 1 agenda\nsome content\nmore text"])
    chunks = chunk_text(pages)
    for chunk in chunks:
        assert chunk.char_count == len(chunk.text)


def test_chunk_text_consent_agenda_detected():
    text = "Consent Agenda\nItem A: Approve minutes\nItem B: Approve budget transfer"
    pages = make_pages([text])
    chunks = chunk_text(pages)
    headers = [c.detected_header for c in chunks if c.detected_header]
    assert any("Consent Agenda" in h for h in headers)


def test_chunk_text_public_hearing_detected():
    text = "PUBLIC HEARING\nZoning case 2024-001\nApplicant requests rezoning"
    pages = make_pages([text])
    chunks = chunk_text(pages)
    headers = [c.detected_header for c in chunks if c.detected_header]
    assert any("PUBLIC HEARING" in h for h in headers)


def test_chunk_text_context_overlap_in_subsequent_chunk():
    """Subsequent chunks should carry some context from the previous segment."""
    lines = ["preamble " + str(i) for i in range(20)]
    preamble = "\n".join(lines)
    text = f"{preamble}\nItem 7 New Topic\nNew topic content"
    pages = make_pages([text])
    chunks = chunk_text(pages)
    item7_chunks = [c for c in chunks if c.detected_header and "Item 7" in c.detected_header]
    assert item7_chunks
    # The chunk should contain the header line
    assert "Item 7" in item7_chunks[0].text
