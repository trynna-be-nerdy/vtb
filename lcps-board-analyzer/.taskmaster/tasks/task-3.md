# Task 3: Gemma 4 integration: implement and test all 3 prompts via Ollama

**Status:** pending
**Priority:** high
**Dependencies:** 1

## Description
This is the critical unblock for the entire project. Get Gemma 4 returning reliable, valid JSON from real LCPS document text using all 3 prompts.

## Implementation Details
1. Locate `backend/pipeline/gemma.py` — verify the 3 prompt templates (PROMPT_1_TEMPLATE, PROMPT_2_TEMPLATE, PROMPT_3_TEMPLATE)
2. Download a real LCPS board meeting agenda PDF from https://go.boarddocs.com/vsba/loudoun/Board.nsf/Public
3. Extract one agenda item section manually (copy ~500 chars of text from the PDF)
4. Write a test script `backend/tests/test_gemma.py`:
   ```python
   from pipeline.gemma import analyze_chunk, classify_item, generate_meeting_overview

   TEST_CHUNK = """AGENDA ITEM 3.1 - BUDGET AMENDMENT FY2026..."""

   # Test Prompt 1
   result1 = analyze_chunk(TEST_CHUNK)
   assert 'title' in result1
   assert 'summary' in result1
   assert isinstance(result1['decisions'], list)
   print('Prompt 1 OK:', result1['title'])

   # Test Prompt 2
   result2 = classify_item(result1['summary'])
   assert result2['primary_category'] in CATEGORY_SLUGS
   assert result2['urgency'] in ['routine', 'notable', 'significant']
   assert isinstance(result2['fiscal_impact'], bool)
   print('Prompt 2 OK: category =', result2['primary_category'])

   # Test Prompt 3
   result3 = generate_meeting_overview([result1['summary']])
   assert 'meeting_overview' in result3
   assert isinstance(result3['top_decisions'], list)
   print('Prompt 3 OK:', result3['meeting_overview'][:100])
   ```
5. Run the test: `cd backend && python tests/test_gemma.py`
6. If Gemma returns malformed JSON: adjust prompt wording to reinforce 'return ONLY valid JSON, no markdown, no backticks'
7. Confirm retry logic works: temporarily break the model name, verify GemmaError is raised after max retries

## Test Strategy
All 3 prompts return valid JSON matching their expected schemas. Prompt 2 returns a valid category slug. Prompt 3 returns a non-empty meeting_overview string. Retry logic raises GemmaError after 3 failed attempts.
