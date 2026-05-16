# View the Board

**Plain-English summaries of every Loudoun County government meeting — powered by Gemma 4, linked to every official source.**

View the Board automatically scrapes, processes, and publishes AI-generated summaries of Board of Supervisors, Planning Commission, LCPS School Board, and Advisory Board meetings so residents can understand local government without reading dense PDF agendas.

---

## Problem Statement

Loudoun County government produces thousands of pages of agenda documents per year across five boards. Most residents never engage because the materials are written in bureaucratic language, buried in PDFs, and spread across multiple portals. This creates an information gap that disproportionately affects residents without time or expertise to parse government documents.

**View the Board** closes that gap: every meeting agenda is automatically converted to plain English, categorised, and searchable — the same day it's posted.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PIPELINE WORKER                             │
│                                                                     │
│  Scraper ──► PDF Downloader ──► pdfplumber ──► Chunker             │
│                                                                     │
│  Chunk ──► Gemma 4 Prompt 1 (rewrite) ──► Pydantic validation      │
│         ──► Gemma 4 Prompt 2 (classify) ──► DB write               │
│                                                                     │
│  All chunks done ──► Gemma 4 Prompt 3 (meeting overview) ──► DB    │
│                  ──► Redis Pub/Sub publish ──► WebSocket clients    │
└─────────────────────────────────────────────────────────────────────┘
            │ asyncpg                          │ Redis
┌───────────▼──────────┐           ┌───────────▼──────────┐
│   PostgreSQL 16       │           │     Redis 7           │
│   (meetings,          │           │   cache-aside 15 min  │
│    agenda_items,      │           │   pub/sub: vtb:updates│
│    tsvector search)   │           └──────────────────────┘
└───────────┬───────────┘                      │
            │                                  │ WebSocket
┌───────────▼──────────────────────────────────▼──────────┐
│                    FASTAPI BACKEND                        │
│   GET /api/meetings  GET /api/search  POST /pipeline     │
│   GET /api/categories  GET /api/health  WS /ws/updates   │
└───────────────────────────┬──────────────────────────────┘
                            │ HTTP + WS
┌───────────────────────────▼──────────────────────────────┐
│               NEXT.JS 15 FRONTEND (ISR 60s)               │
│   Navbar · Intro · Board Sections · Official Sources      │
│   Newsletter · Footer · Real-time toast notifications     │
└──────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| AI / LLM | Gemma 4 via Ollama | Local inference, no API costs, structured JSON output |
| Frontend | Next.js 15, TypeScript, DaisyUI | ISR for freshness, server components for DB-direct fetches |
| Backend | FastAPI, Python 3.13 | Async-first, auto-generated OpenAPI docs |
| Database | PostgreSQL 16 | Full-text search (`tsvector`), JSONB for key figures |
| Cache | Redis 7 | 15-min cache-aside on all GET endpoints |
| Real-time | WebSocket + Redis Pub/Sub | Multi-worker safe, horizontal scaling |
| PDF parsing | pdfplumber | Reliable text extraction from government PDFs |
| Migrations | Alembic | Versioned schema management |
| Containers | Docker Compose | Single-command local setup |

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Ollama](https://ollama.com/) installed locally
- Node.js 20+ (for frontend dev server)

### 1. Pull the model

```bash
ollama pull gemma4:4b
```

> **Note:** The pipeline uses `gemma4:4b` by default for speed. Set `OLLAMA_MODEL=gemma4:26b` in `.env` for higher quality output.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set a PIPELINE_API_KEY
```

### 3. Start all backend services

```bash
docker compose up
```

This starts PostgreSQL, Redis, runs database migrations + source seeding, then launches the FastAPI API and pipeline worker.

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

**API docs:** [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://vtb:vtbpassword@localhost:5432/vtb` | Async DB URL for FastAPI and pipeline |
| `ALEMBIC_DATABASE_URL` | `postgresql+psycopg://vtb:vtbpassword@localhost:5432/vtb` | Sync DB URL for Alembic migrations |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `gemma4:4b` | Model name for all LLM calls |
| `PIPELINE_API_KEY` | `change-me-in-production` | Secret for `POST /api/pipeline/trigger` |

---

## API Endpoints

All endpoints return JSON. GET endpoints are Redis-cached.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/health` | Pipeline status, queue depth, items this month |
| `GET` | `/api/meetings` | Paginated meeting list — filter by `?board=board-of-supervisors` |
| `GET` | `/api/meetings/{id}` | Full meeting detail with all agenda items |
| `GET` | `/api/categories` | All categories with item counts |
| `GET` | `/api/categories/{slug}` | Paginated items for a category |
| `GET` | `/api/search?q=` | Full-text search across titles, summaries, and decisions |
| `POST` | `/api/pipeline/trigger` | Trigger a pipeline run (requires `X-API-Key` header) |
| `WS` | `/ws/updates` | WebSocket stream of real-time pipeline events |

### Board slugs

`board-of-supervisors` · `planning-commission` · `lcps-school-board` · `advisory-boards`

### Category slugs

`schools-education` · `school-construction` · `budget-finance` · `transportation` · `zoning-land-use` · `public-safety` · `policy-governance` · `equity-inclusion` · `technology` · `community-parks` · `personnel` · `general`

---

## Database Schema

```
meetings
  id, title, board_slug, meeting_date
  meeting_overview, top_decisions[], fiscal_total
  total_items, fiscal_items, processing_status
  source_url, source_pdf_url, next_meeting_notes

agenda_items
  id, meeting_id, title, summary
  primary_category, secondary_tags[], urgency
  fiscal_impact, affects_schools[]
  decisions[], action_items[], key_figures (JSONB)
  source_pdf_url, page_range
  search_vector (tsvector — auto-updated by trigger)

sources
  id, name, base_url, scraper_type, enabled

seen_documents
  id, url, sha256, status (pending|processing|completed|failed)

pipeline_runs
  id, started_at, status, metrics (JSONB)
```

Full schema: [`backend/db/models.py`](backend/db/models.py) · Migrations: [`alembic/versions/`](alembic/versions/)

---

## Gemma 4 Prompt Engineering

Three sequential prompts process each agenda item:

### Prompt 1 — Plain-English Rewrite

Converts raw extracted PDF text into a structured plain-English summary. Output: `title`, `summary` (2–4 sentences), `decisions[]`, `action_items[]`, `key_figures` (amounts, vote tallies, dates, school names).

### Prompt 2 — Classification

Takes the rewritten summary and assigns it a category slug, urgency level (`routine` / `notable` / `significant`), fiscal impact flag, and affected schools list.

### Prompt 3 — Meeting Overview

After all items are processed, synthesises the full set of item summaries into a meeting-level narrative overview and extracts the top 3 decisions.

All prompts use Ollama's structured JSON output mode (`"format": <json-schema>`) to enforce valid responses, with automatic retry on parse failure.

---

## Production Deployment

### Frontend → Vercel

1. Push to GitHub, then connect the repo in the [Vercel dashboard](https://vercel.com/new).
2. Set **Root Directory** to `frontend/`.
3. Add environment variables in the Vercel dashboard:
   - `DATABASE_URL` — Neon or another external PostgreSQL URL
   - `REDIS_URL` — Upstash Redis URL (`rediss://...`)
   - `CRON_SECRET` — random secret for the `/api/cron/pipeline` endpoint
4. Vercel auto-deploys on every push to `main`.

### Backend → Render

The `render.yaml` blueprint in the repo defines two services:
- **vtb-api**: FastAPI web service (health check at `/api/health`)
- **vtb-pipeline-worker**: background worker running APScheduler

Deploy via [Render Blueprint](https://render.com/docs/blueprint-spec):
1. Connect your GitHub repo in the Render dashboard.
2. Render will read `render.yaml` and create both services automatically.
3. Set environment variables in the Render dashboard for each service:
   - `DATABASE_URL`, `REDIS_URL`, `OLLAMA_BASE_URL`, `PIPELINE_API_KEY`

### Shared infrastructure

- **PostgreSQL**: [Neon](https://neon.tech) free tier — one connection string works from both Vercel and Render.
- **Redis**: [Upstash](https://upstash.com) free tier — use the `rediss://` TLS URL for external access.

### Connecting Render to local Ollama (ngrok)

The pipeline worker on Render needs to reach the Ollama server running on your local machine:

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 11434 --host-header=localhost:11434
```

Copy the `https://xxxx.ngrok-free.app` URL and set it as `OLLAMA_BASE_URL` in the Render dashboard for the `vtb-pipeline-worker` service.

> **Alternative:** Run the pipeline worker locally (it writes to the shared DB/Redis) and only deploy the FastAPI API to Render for serving the read-only API routes.

---

## Quality Metrics

| Metric | How measured |
|---|---|
| Classification accuracy | Manual review of 50 items across all 12 categories |
| Summary readability | Flesch-Kincaid grade level target: 8th grade or lower |
| JSON parse failure rate | Tracked in pipeline logs; target < 5% before retry |
| Deduplication | SHA-256 hash of source URL; re-scrapes are no-ops |
| Cache hit rate | Redis `INFO stats` → `keyspace_hits / (hits + misses)` |
| API latency (p99) | Uvicorn access logs; target < 200ms on cached responses |

---

## Out of Scope (MVP)

- User accounts and personalised alerts
- Email delivery of newsletter digests (UI only, no backend)
- "How to speak at a board meeting" guide content
- Mobile-optimised experience (responsive but not native)
- Historical data before project start date
- Loudoun County Economic Development Authority and other minor bodies

---

## Project Structure

```
VtB/
├── frontend/               # Next.js 15 app
│   ├── app/                # App Router pages
│   ├── components/         # Shared React components
│   └── lib/                # Data fetching and types
├── backend/
│   ├── api/                # FastAPI app, routes, schemas
│   ├── cache/              # Redis client and helpers
│   ├── db/                 # SQLAlchemy models, Alembic migrations
│   ├── llm/                # Gemma 4 / Ollama client + prompts
│   ├── pipeline/           # Scrapers, PDF processor, worker
│   └── pubsub/             # Redis Pub/Sub publisher
├── alembic/                # Migration scripts
├── scripts/                # init-db.sh and utilities
├── Dockerfile.api          # FastAPI container
├── Dockerfile.pipeline     # Pipeline worker container
├── docker-compose.yml      # Full local stack
└── .env.example            # Environment variable template
```

---

## License

MIT — see [LICENSE](LICENSE).

Data sourced from Loudoun County Government ([loudoun.gov/meetings](https://loudoun.gov/meetings)) and LCPS ([lcps.org/boarddocs](https://lcps.org/boarddocs)) under public records access. View the Board is not affiliated with Loudoun County Government. AI-generated summaries are for informational purposes; always verify against official sources.
