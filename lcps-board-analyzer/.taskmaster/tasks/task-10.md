# Task 10: FastAPI web server: meetings and categories endpoints with Redis caching

**Status:** pending
**Priority:** high
**Dependencies:** 2, 9

## Description
Stand up the FastAPI web server with the core read endpoints, confirm they serve real data from the database, and verify Redis caching works.

## Implementation Details
1. Locate `backend/app/main.py` — verify all 5 routers are included
2. Start the API server: `uvicorn app.main:app --reload --port 8000`
3. Test each endpoint manually:
   ```bash
   curl http://localhost:8000/ | python3 -m json.tool
   curl 'http://localhost:8000/api/meetings?page=1&page_size=5' | python3 -m json.tool
   curl http://localhost:8000/api/categories | python3 -m json.tool
   curl 'http://localhost:8000/api/categories/budget-finance' | python3 -m json.tool
   curl http://localhost:8000/api/health | python3 -m json.tool
   ```
4. After pipeline has run (task 9): verify meetings endpoint returns real data with meeting_overview populated
5. Verify Redis caching: hit the same endpoint twice, second call should be faster and log 'cache hit'
6. Verify cache invalidation: trigger pipeline, then call meetings endpoint — should return fresh data
7. Test POST /api/pipeline/trigger with correct API key returns {status: 'ok'}
8. Test POST /api/pipeline/trigger with wrong API key returns 401
9. Open http://localhost:8000/docs — verify all endpoints appear with correct schemas

## Test Strategy
All endpoints return 200 with valid JSON. /api/meetings returns items array with meeting_overview populated. /api/health shows last_run_at. Redis cache reduces response time on second call. Swagger UI at /docs shows all routes.
