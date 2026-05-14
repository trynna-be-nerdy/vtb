"""Tests for backend/pipeline/pdf_extractor.py"""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.pipeline.pdf_extractor import (
    PageText,
    PdfExtractionError,
    _detect_boilerplate,
    _strip_boilerplate,
    extract_text,
)


# --- unit tests for helper functions ---

def test_detect_boilerplate_finds_repeated_lines():
    pages = [
        "Page 1\nHeader Text\nContent A",
        "Page 2\nHeader Text\nContent B",
        "Page 3\nHeader Text\nContent C",
    ]
    boilerplate = _detect_boilerplate(pages)
    assert "Header Text" in boilerplate
    assert "Content A" not in boilerplate


def test_detect_boilerplate_skips_on_few_pages():
    pages = ["Line A\nUnique content", "Line A\nOther content"]
    # Only 2 pages — threshold logic returns empty set
    result = _detect_boilerplate(pages)
    # With 2 pages < 3 we get empty set
    assert result == set()


def test_strip_boilerplate_removes_matching_lines():
    text = "Loudoun County\nImportant Content\nLoudoun County"
    boilerplate = {"Loudoun County"}
    cleaned = _strip_boilerplate(text, boilerplate)
    assert "Loudoun County" not in cleaned
    assert "Important Content" in cleaned


def test_strip_boilerplate_empty_set_returns_unchanged():
    text = "All content\nremains"
    assert _strip_boilerplate(text, set()) == text


# --- tests with mocked pdfplumber ---

def _make_mock_pdf(pages_text: list[str], encrypted: bool = False):
    mock_pdf = MagicMock()
    mock_pdf.metadata = {"Encrypt": True} if encrypted else {}
    mock_pages = []
    for i, text in enumerate(pages_text, start=1):
        p = MagicMock()
        p.page_number = i
        p.extract_text.return_value = text
        mock_pages.append(p)
    mock_pdf.pages = mock_pages
    mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
    mock_pdf.__exit__ = MagicMock(return_value=False)
    return mock_pdf


def test_extract_text_returns_page_list(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"fake")

    mock_pdf = _make_mock_pdf(["Page one text", "Page two text", "Page three text"])
    with patch("pdfplumber.open", return_value=mock_pdf):
        result = extract_text(pdf_path)

    assert len(result) == 3
    assert all(isinstance(p, PageText) for p in result)
    assert result[0].page_num == 1
    assert result[1].page_num == 2


def test_extract_text_char_count_matches(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"fake")

    mock_pdf = _make_mock_pdf(["Hello world"])
    with patch("pdfplumber.open", return_value=mock_pdf):
        result = extract_text(pdf_path)

    assert result[0].char_count == len(result[0].text)


def test_extract_text_handles_empty_page(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"fake")

    mock_pdf = _make_mock_pdf(["Content here", "", "More content"])
    # Make second page return None (scanned/image page)
    mock_pdf.pages[1].extract_text.return_value = None

    with patch("pdfplumber.open", return_value=mock_pdf):
        result = extract_text(pdf_path)

    assert len(result) == 3
    assert result[1].text == ""
    assert result[1].char_count == 0


def test_extract_text_raises_on_encrypted(tmp_path):
    pdf_path = tmp_path / "encrypted.pdf"
    pdf_path.write_bytes(b"fake")

    mock_pdf = _make_mock_pdf(["text"], encrypted=True)
    with patch("pdfplumber.open", return_value=mock_pdf):
        with pytest.raises(PdfExtractionError, match="encrypted"):
            extract_text(pdf_path)


def test_extract_text_raises_on_missing_file():
    with pytest.raises(PdfExtractionError, match="not found"):
        extract_text(Path("/nonexistent/path.pdf"))


def test_extract_text_strips_repeated_header(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"fake")

    header = "LOUDOUN COUNTY PUBLIC SCHOOLS"
    pages = [
        f"{header}\nAgenda Item 1 content here",
        f"{header}\nAgenda Item 2 content here",
        f"{header}\nAgenda Item 3 content here",
    ]
    mock_pdf = _make_mock_pdf(pages)
    with patch("pdfplumber.open", return_value=mock_pdf):
        result = extract_text(pdf_path)

    for page in result:
        assert header not in page.text
