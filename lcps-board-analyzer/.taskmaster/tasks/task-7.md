# Task 7: Web scrapers: LCPS BeautifulSoup scraper and Loudoun BOS Legistar API client

**Status:** pending
**Priority:** high
**Dependencies:** 1

## Description
Implement and verify both document discovery scrapers so the pipeline can find real PDFs from both sources.

## Implementation Details
1. Locate `backend/pipeline/scraper.py` — verify `scrape_lcps()` and `scrape_loudoun_bos()`
2. Test the LCPS scraper:
   ```python
   import httpx
   from pipeline.scraper import scrape_lcps
   with httpx.Client() as client:
       docs = scrape_lcps(client)
   print(f'Found {len(docs)} LCPS docs')
   for d in docs[:3]:
       print(d.url, d.title)
   ```
3. If lcps.org blocks the request, inspect the HTML structure and fix the selector. Try the BoardDocs API: `GET https://go.boarddocs.com/vsba/loudoun/Board.nsf/AJAX-PublicMeetingList`
4. Test the Loudoun BOS Legistar client:
   ```python
   import httpx
   from pipeline.scraper import scrape_loudoun_bos
   with httpx.Client() as client:
       docs = scrape_loudoun_bos(client)
   print(f'Found {len(docs)} BOS docs')
   ```
5. Verify Legistar API returns real event data: `curl 'https://webapi.legistar.com/v1/loudoun/events?$top=5'`
6. Verify polite_get() adds the 4-second delay
7. Verify browser-like User-Agent headers are set on all requests
8. Test `discover_all_documents()` returns combined list

## Test Strategy
scrape_lcps() returns ≥ 1 DiscoveredDocument with a .pdf URL. scrape_loudoun_bos() returns ≥ 1 DiscoveredDocument. Both scrapers handle HTTP errors gracefully (log warning, return empty list).
