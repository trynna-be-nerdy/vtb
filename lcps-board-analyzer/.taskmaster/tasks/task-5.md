# Task 5: Agenda item chunker: split PDF text into per-item sections

**Status:** pending
**Priority:** high
**Dependencies:** 4

## Description
Implement and tune the chunker that splits raw PDF text on agenda item headers and caps each chunk at 2,000 characters.

## Implementation Details
1. Locate `backend/pipeline/chunker.py` — verify `split_into_chunks(pages: list[str]) -> list[str]`
2. The regex must match these patterns (case-insensitive):
   - `AGENDA ITEM 3` / `AGENDA ITEM 3.1`
   - `ITEM 4` / `ITEM 4.2`
   - `PUBLIC HEARING`
   - `ACTION ITEM 2`
   - `CONSENT AGENDA`
   - `INFORMATION ITEM 1`
3. Test with the extracted pages from task 4:
   ```python
   from pipeline.chunker import split_into_chunks
   chunks = split_into_chunks(pages)
   print(f'{len(chunks)} chunks found')
   for i, c in enumerate(chunks[:3]):
       print(f'--- Chunk {i+1} ({len(c)} chars) ---')
       print(c[:200])
   ```
4. Verify chunks are capped at PDF_CHUNK_MAX_CHARS (2000)
5. Verify short chunks (<100 chars) are dropped
6. If a real LCPS document produces 0 chunks, inspect the raw text and adjust the regex pattern
7. Test the paragraph-boundary sub-chunking for long items

## Test Strategy
A real LCPS agenda PDF produces at least 3 chunks. No chunk exceeds 2,000 chars. Chunks shorter than 100 chars are excluded. Each chunk contains readable agenda item text.
