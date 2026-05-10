# Task 15: Docker Compose full stack, ngrok tunnel, Vercel deploy, and hackathon submission prep

**Status:** pending
**Priority:** high
**Dependencies:** 9, 11, 14

## Description
Get everything running end-to-end in Docker Compose, deploy the frontend to Vercel, wire it to the local backend via ngrok, and complete all hackathon submission requirements.

## Implementation Details
1. **Docker Compose full stack**:
   ```bash
   docker compose up --build
   ```
   - Verify all 4 services start: postgres, redis, api, pipeline
   - Run migrations inside the api container: `docker compose exec api alembic upgrade head`
   - Seed sources table: `docker compose exec api python -c 'from scripts.seed import seed; seed()'` (create seed script if needed)
   - Verify GET http://localhost:8000/api/health returns ok

2. **ngrok tunnel** (for Vercel → local backend):
   ```bash
   ngrok http 8000
   # Copy the https URL e.g. https://abc123.ngrok.io
   ```

3. **Vercel deployment**:
   - Push frontend to GitHub
   - Connect repo to Vercel
   - Set env vars in Vercel dashboard:
     - NEXT_PUBLIC_API_URL=https://abc123.ngrok.io
     - NEXT_PUBLIC_WS_URL=wss://abc123.ngrok.io/ws/updates
   - Deploy and verify live URL loads real data

4. **Demo video** (< 3 min):
   - Show a real LCPS PDF URL being discovered
   - Show pipeline log output as it processes
   - Show the live blog card appear on the public Vercel URL
   - Record with OBS or Loom

5. **README completeness check**:
   - Architecture diagram present
   - All 3 Gemma 4 prompts documented
   - Setup commands work on a clean machine
   - Demo video link included
   - Screenshots of the live UI

6. **Kaggle Notebook** technical write-up — paste from Notion docs

7. **Submission checklist**:
   - [ ] GitHub repo is public
   - [ ] Live Vercel URL accessible without login
   - [ ] Kaggle Notebook public
   - [ ] Track: Digital Equity selected
   - [ ] Submit on Kaggle before May 18, 2026 at 11:59 PM UTC

## Test Strategy
docker compose up starts all 4 services with no errors. Live Vercel URL shows real meeting cards loaded from local FastAPI via ngrok. Demo video shows full real-document flow in under 3 minutes. Kaggle submission form completed and confirmed.
