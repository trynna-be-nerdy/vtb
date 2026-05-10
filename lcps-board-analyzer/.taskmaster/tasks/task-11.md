# Task 11: FastAPI search endpoint and WebSocket real-time updates

**Status:** pending
**Priority:** medium
**Dependencies:** 10

## Description
Implement and test the PostgreSQL full-text search endpoint and the WebSocket connection that pushes live notifications to frontend clients.

## Implementation Details
1. Test the search endpoint:
   ```bash
   curl 'http://localhost:8000/api/search?q=budget' | python3 -m json.tool
   curl 'http://localhost:8000/api/search?q=transportation+buses' | python3 -m json.tool
   ```
2. Verify search results are ranked by ts_rank (most relevant first)
3. Verify search uses the `search_vector` GIN index (check EXPLAIN ANALYZE output)
4. Test WebSocket connection:
   ```python
   import asyncio, websockets, json

   async def test_ws():
       async with websockets.connect('ws://localhost:8000/ws/updates') as ws:
           # Trigger a pipeline run to generate a broadcast
           print('Connected, waiting for message...')
           msg = await asyncio.wait_for(ws.recv(), timeout=60)
           print('Received:', json.loads(msg))

   asyncio.run(test_ws())
   ```
5. Verify WebSocket broadcast arrives when pipeline publishes a new item
6. Verify WebSocket reconnects after server restart (test client-side reconnect logic)
7. Test search with no results returns empty items array and total=0
8. Test search with q shorter than 2 chars returns 422

## Test Strategy
Search for a keyword that appears in a real agenda item returns that item. ts_rank orders results correctly. WebSocket client receives {type: 'new_item'} message when pipeline runs. Edge cases return correct HTTP status codes.
