# Task 4: PDF extractor: download and pdfplumber text extraction

**Status:** pending
**Priority:** high
**Dependencies:** 1

## Description
Implement and verify the PDF downloader and pdfplumber extractor that converts government PDFs into page-by-page text.

## Implementation Details
1. Locate `backend/pipeline/extractor.py` — verify `download_pdf(url)` and `extract_text_from_bytes(pdf_bytes)` functions
2. Test with a real LCPS PDF URL:
   ```python
   from pipeline.extractor import download_pdf, extract_text_from_bytes
   pdf_bytes, sha256 = download_pdf('https://...real-lcps-url.pdf')
   print(f'Downloaded {len(pdf_bytes)} bytes, sha256: {sha256[:12]}')
   pages = extract_text_from_bytes(pdf_bytes)
   print(f'Extracted {len(pages)} pages')
   print('Page 1 preview:', pages[0][:300])
   ```
3. Confirm MIME type validation rejects non-PDF URLs
4. Confirm SHA-256 hashing is consistent (same file = same hash)
5. Handle edge case: some LCPS PDFs use image-based scans — log a warning if text extraction returns empty pages (OCR is out of scope for v1)
6. Ensure temp file cleanup happens even on exceptions (use try/finally)

## Test Strategy
download_pdf() returns bytes + 64-char hex sha256. extract_text_from_bytes() returns a non-empty list of strings. ValueError raised for non-PDF URLs. Temp files are cleaned up.
