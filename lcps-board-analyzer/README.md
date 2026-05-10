# LCPS Board Meeting Analyzer

> **Gemma 4 Good Hackathon · Kaggle × Google DeepMind · Digital Equity Track · Deadline May 18, 2026**

Gemma 4 reads every official LCPS and Loudoun County board meeting document and rewrites it in plain English — so any resident can understand what was decided in 2 minutes instead of 2 hours.

## What It Does

An automated pipeline that runs every 6 hours:
1. Scrapes new PDFs from [lcps.org](https://lcps.org) and Loudoun County BOS (via Legistar API)
2. Sends each agenda item through **Gemma 4** to be rewritten in plain English
3. Classifies it into one of 12 topic categories
4. Publishes it instantly to the public website

**Resident experience:** Open a URL → see what the board decided → done in 2 minutes. No PDF required.

## Stack

| Layer | Technology |
|---|---|
| LLM | Gemma 4 E4B via Ollama (local) |
| Backend | FastAPI + PostgreSQL 16 + Redis |
| Pipeline | Python + pdfplumber + APScheduler |
| Frontend | Next.js 14 + TypeScript + HeroUI + Tailwind |
| Hosting | Vercel (frontend) · Render (backend) |

## Quick Start

### Prerequisites
- Docker Desktop
- Ollama with Gemma 4: `ollama pull gemma4:4b`
- Node.js 20+

### 1. Clone and configure
```bash
git clone <repo-url> lcps-board-analyzer
cd lcps-board-analyzer
cp .env.example .env
```

### 2. Start backend services
```bash
docker compose up
```
This starts PostgreSQL, Redis, the FastAPI server (port 8000), and the pipeline worker.

### 3. Run database migrations
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

### 4. Start the frontend
```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

### Production deployment
```bash
# Expose local FastAPI via ngrok for Vercel to reach
ngrok http 8000

# Set in Vercel dashboard:
# NEXT_PUBLIC_API_URL = https://your-ngrok-url.ngrok.io
# NEXT_PUBLIC_WS_URL  = wss://your-ngrok-url.ngrok.io/ws/updates
```

## Architecture

```
[lcps.org / loudoun.gov]
        ↓
[Pipeline Worker — separate process]
  Scraper → pdfplumber → Chunker → Gemma 4 → PostgreSQL → Redis invalidate
        ↓ writes only
[PostgreSQL — managed cloud]
        ↑ reads only
[FastAPI Web Servers — stateless]
        ↑
[Redis Cache — 15-min TTL]
        ↑
[Vercel CDN — Next.js ISR frontend]
        ↑
[Residents in browsers]
```

## The 3 Gemma 4 Prompts

**Prompt 1 — Content rewrite** (per agenda item):
Returns `title`, `summary`, `decisions[]`, `action_items[]`, `key_figures`

**Prompt 2 — Category classification** (per rewritten summary):
Returns `primary_category`, `secondary_tags[]`, `urgency`, `fiscal_impact`, `affects_schools[]`

**Prompt 3 — Meeting overview** (once per document):
Returns `meeting_overview`, `top_decisions[]`, `fiscal_total`, `next_meeting_notes`

All prompts return only valid JSON. Retry logic handles malformed output (up to 2 retries).

## API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/api/meetings` | Paginated meetings |
| GET | `/api/meetings/{id}` | Full meeting detail |
| GET | `/api/categories` | All 12 categories with item counts |
| GET | `/api/categories/{slug}` | Paginated category feed |
| GET | `/api/search?q=` | Full-text search |
| GET | `/api/health` | Pipeline status |
| POST | `/api/pipeline/trigger` | Manual trigger (API key) |
| WS | `/ws/updates` | Real-time push |

## The 12 Categories

`schools-education` · `school-construction` · `budget-finance` · `transportation` · `zoning-land-use` · `public-safety` · `policy-governance` · `equity-inclusion` · `technology` · `community-parks` · `personnel` · `general`

## Project Structure

```
lcps-board-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings
│   │   ├── database.py       # Async SQLAlchemy
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routers/          # API route handlers
│   │   ├── schemas/          # Pydantic response models
│   │   └── services/         # Cache (Redis) + WebSocket
│   ├── pipeline/
│   │   ├── worker.py         # APScheduler entry point
│   │   ├── scraper.py        # lcps.org + Legistar API
│   │   ├── extractor.py      # pdfplumber
│   │   ├── chunker.py        # Agenda item splitter
│   │   ├── gemma.py          # The 3 Gemma 4 prompts
│   │   ├── validator.py      # 10-check quality gate
│   │   └── publisher.py      # DB write + Redis + WebSocket
│   ├── alembic/              # DB migrations
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                  # Next.js 14 App Router
│   │   ├── page.tsx          # Homepage
│   │   ├── meetings/[id]/    # Meeting detail
│   │   ├── category/[slug]/  # Category feed
│   │   └── search/           # Search page
│   ├── components/
│   │   ├── layout/           # Navbar + CategoryTicker
│   │   └── cards/            # MeetingCard
│   ├── lib/                  # API client + constants
│   ├── hooks/                # useWebSocket + useDebounce
│   └── types/                # TypeScript interfaces
├── docker-compose.yml
├── .env.example
└── README.md
```

## Hackathon Submission Checklist

- [ ] GitHub repo is public with complete README
- [ ] All 3 Gemma 4 prompts documented in technical write-up
- [ ] Docker Compose working on a clean machine (`docker compose up`)
- [ ] Demo video: real LCPS PDF → real blog card on live website (< 3 min)
- [ ] Kaggle Notebook write-up complete and public
- [ ] Live Vercel URL accessible without login
- [ ] Track: Digital Equity
- [ ] Submitted before May 18, 2026 at 11:59 PM UTC

## License

MIT
