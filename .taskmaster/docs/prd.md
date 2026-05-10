# LCPS Board Meeting Analyzer — Product Requirements Document

**Version:** 1.2 | **Deadline:** May 18, 2026 at 11:59 PM UTC | **Track:** Digital Equity | **Hackathon:** Gemma 4 Good (Kaggle × Google DeepMind)

---

## 1. Overview

The LCPS Board Meeting Analyzer is a fully automated civic AI web application that monitors the Loudoun County Public Schools (LCPS) board meetings website and Loudoun County Board of Supervisors site. It uses **Gemma 4** (running locally via Ollama) to read every official document and rewrite it in plain English, then automatically publishes the content to a public blog-style website organized by topic — so any resident can understand what their local government decided without reading a 40-page PDF.

**One-line description:** Gemma 4 reads the official school board page so residents don't have to — then adds the content to the site, already organized, tagged, and written in plain English.

---

## 2. Problem

Loudoun County is one of the fastest-growing counties in Virginia. Its Board of Supervisors and LCPS School Board meet regularly and produce 30–80 page documents per meeting in legal/bureaucratic language. No summary layer exists. The average resident has 2–5 minutes, not 3 hours. Documents are raw PDFs with no organization by topic.

---

## 3. Solution

An automated pipeline that runs every 6 hours:
1. Finds new PDFs posted by LCPS and Loudoun County
2. Sends each agenda item through Gemma 4 to be rewritten in plain English
3. Classifies it into one of 12 topic categories
4. Publishes it to the correct section of a public website

---

## 4. Technical Architecture

### System Split (non-negotiable)
The pipeline and web server run as completely separate processes. A Gemma 4 call takes 15–30 seconds — it must never block FastAPI request handlers.

```
[lcps.org / loudoun.gov]
        ↓
[Pipeline Worker — separate process]
  Scraper → pdfplumber → Chunker → Gemma 4 → PostgreSQL → Redis invalidate
        ↓ writes only
[PostgreSQL — managed cloud]
        ↑ reads only
[FastAPI Web Servers — stateless instances]
        ↑
[Redis Cache — 15-min TTL]
        ↑
[Vercel CDN — Next.js ISR frontend]
        ↑
[Residents in browsers]
```

### Full Stack

| Layer | Technology |
|---|---|
| LLM | Gemma 4 E4B via Ollama (RTX 4050, 6GB VRAM) |
| Scraper | Python requests + BeautifulSoup4 |
| PDF parsing | pdfplumber |
| Scheduler | APScheduler — in-process on pipeline worker, every 6 hours |
| API server | FastAPI + uvicorn (stateless, horizontally scalable) |
| Database | PostgreSQL 16 (Supabase or Neon managed) |
| Cache | Redis (Upstash serverless) |
| Real-time | FastAPI WebSockets + Redis Pub/Sub for multi-instance broadcast |
| Frontend framework | Next.js 14 App Router with ISR |
| Frontend language | TypeScript |
| UI components | HeroUI v2 + shadcn/ui |
| Styling | Tailwind CSS v3 |
| Animations | framer-motion |
| Data fetching | TanStack Query |
| Icons | Lucide React |
| Frontend hosting | Vercel free tier |
| Backend hosting | Local (demo) → Render free tier (production) |
| Containers | Docker Compose — PostgreSQL + Redis + FastAPI + pipeline worker |

---

## 5. Database Schema

### Tables

**sources** — config per monitored website (lcps.org, loudoun.gov)

**seen_documents** — deduplication: URL + SHA-256 hash + processing status (pending/processing/completed/failed)

**meetings** — one row per board meeting, contains Gemma 4 generated overview:
- `meeting_date`, `title`, `source_url`, `source_pdf_url`
- `meeting_overview`, `top_decisions[]`, `fiscal_total`, `next_meeting_notes`
- `total_items`, `fiscal_items`, `processing_status`

**agenda_items** — one row per agenda item (the core content unit):
- `title` — plain English card headline
- `summary` — 2–4 sentence summary
- `primary_category` — one of 12 slugs
- `secondary_tags[]` — sub-topic tags
- `decisions[]` — decisions made in plain language
- `action_items[]` — next steps
- `key_figures` — JSONB: dollar amounts, vote tallies, dates, schools
- `urgency` — routine / notable / significant
- `fiscal_impact` — boolean
- `affects_schools[]` — school names
- `source_pdf_url` — link to original government PDF
- `page_range` — "pp. 12–15" reference
- `search_vector` — tsvector for PostgreSQL full-text search (auto-updated by trigger)

**supporting_documents** — attachments linked to meetings

**pipeline_runs** — audit log of every automated run

---

## 6. The 3 Gemma 4 Prompts

All prompts must return **only valid JSON** — no markdown, no backticks, no preamble. Retry logic handles malformed output up to 2 retries.

### Prompt 1 — Content Rewrite (per agenda item chunk)
Input: raw chunk of official board document text (max 2,000 chars)
Output:
```json
{
  "title": "plain English topic title, max 10 words",
  "summary": "2-4 sentences for a general adult audience, no jargon",
  "decisions": ["exact decision or vote in plain language"],
  "action_items": ["next step or follow-up action"],
  "key_figures": {
    "amounts": ["dollar amounts mentioned"],
    "vote_tallies": ["vote results like '5-2 approved'"],
    "dates": ["specific dates mentioned"],
    "schools": ["specific school names mentioned"]
  }
}
```

### Prompt 2 — Section + Tag Assignment (per rewritten summary)
Input: the rewritten summary from Prompt 1
Output:
```json
{
  "primary_category": "one of 12 slugs",
  "secondary_tags": ["specific sub-topic tags"],
  "urgency": "routine OR notable OR significant",
  "fiscal_impact": true,
  "affects_schools": ["specific school names if mentioned"]
}
```

### Prompt 3 — Meeting Overview (once per document, after all chunks)
Input: all rewritten summaries from one meeting
Output:
```json
{
  "meeting_overview": "3-5 sentence overview of the entire meeting",
  "top_decisions": ["the 3 most significant decisions made"],
  "fiscal_total": "total spending approved or null",
  "next_meeting_notes": "any follow-up items mentioned or null"
}
```

---

## 7. The 12 Content Categories

Every agenda item routes to exactly one:

| Slug | Label | Covers |
|---|---|---|
| `schools-education` | Schools & Education | Curriculum, testing, calendars, special ed |
| `school-construction` | School Construction | New buildings, renovations, CIP projects |
| `budget-finance` | Budget & Finance | Budgets, audits, grants, debt, fiscal votes |
| `transportation` | Transportation | Buses, VDOT, roads, sidewalks, traffic |
| `zoning-land-use` | Zoning & Land Use | Rezonings, special exceptions, proffering |
| `public-safety` | Public Safety | Safety protocols, SRO, emergency plans |
| `policy-governance` | Policy & Governance | Board policy, ethics, appointments |
| `equity-inclusion` | Equity & Inclusion | Title IX, language access, equity audits |
| `technology` | Technology | EdTech, cybersecurity, FERPA, AI policy |
| `community-parks` | Community & Parks | Facility use, afterschool, parks |
| `personnel` | Personnel | Staff, compensation, labor agreements |
| `general` | General | Catch-all for unclassified items |

---

## 8. API Endpoints

| Method | Route | Description |
|---|---|---|
| GET | `/api/meetings` | Paginated meetings, newest first |
| GET | `/api/meetings/{id}` | Full meeting with all agenda items + documents |
| GET | `/api/categories` | All 12 categories with item counts |
| GET | `/api/categories/{slug}` | Paginated item feed for one category |
| GET | `/api/search?q=` | Full-text search across title + summary + decisions |
| GET | `/api/health` | Pipeline status, last run time, queue depth |
| POST | `/api/pipeline/trigger` | Manually trigger a pipeline run (API key required) |
| WS | `/ws/updates` | Real-time push when new items are processed |

---

## 9. Frontend Features

### Homepage
- Frosted glass sticky navbar with dark mode toggle
- Auto-scrolling category ticker bar below navbar (framer-motion)
- Hero section with one-line app description
- 12-category navigation grid with item counts
- Masonry card grid of latest meeting cards (editorial newspaper layout)
- Meeting cards: source badge, date, title, 2-sentence summary preview, top decisions, fiscal icon, source PDF link

### Meeting Detail Page (`/meetings/{id}`)
- Full meeting overview (Gemma 4 Prompt 3 output)
- Quick stats bar: item count, fiscal items, total spending
- Top 3 decisions highlighted
- Expandable accordion agenda items: full summary → decisions → action items → page reference → source link
- Supporting documents section

### Category Pages (`/category/{slug}`)
- 12 sections, one per category slug
- Paginated item feed
- Sub-tag filter chips
- Fiscal toggle filter

### Search Page (`/search`)
- Full-text search across all content
- Debounced query input (400ms)
- PostgreSQL tsvector ranked results

### Live Updates
- WebSocket connection in Navbar
- Toast notification when new content is published by pipeline

### Design System
- Dark mode first-class (deep navy `#0a0f1e`, not pure black)
- Serif display font (Georgia) for meeting titles, Inter for UI
- 12 category accent colors
- Urgency border colors: slate (routine), amber (notable), red (significant)
- Masonry grid layout (CSS columns)
- framer-motion animations throughout

---

## 10. Pipeline Worker

### Full flow (runs every 6 hours as a separate process):
1. **Scraper** — hits lcps.org (BeautifulSoup4) and loudoun.gov (Legistar JSON API)
2. **Deduplicator** — checks `seen_documents` by URL + SHA-256; skips unchanged docs
3. **Downloader** — fetches PDFs via httpx, validates MIME type
4. **Extractor** — pdfplumber extracts text page-by-page
5. **Chunker** — splits on agenda item headers, caps at 2,000 chars per chunk
6. **Gemma 4 Pass 1** — Prompt 1 per chunk: content rewrite
7. **Gemma 4 Pass 2** — Prompt 2 on rewritten summary: classification
8. **Validator** — 10 Python quality checks before any DB write
9. **DB write** — atomic PostgreSQL transaction, search_vector trigger fires
10. **Cache invalidation** — Redis keys for affected feeds deleted
11. **WebSocket broadcast** — Redis Pub/Sub notifies all connected frontend clients
12. **Post-processing** — Prompt 3 generates meeting-level overview after all chunks complete

### Scraping rules
- Browser-like headers, 4-second delay between requests, never parallel
- Legistar API for Loudoun BOS (structured JSON — no scraping needed)
- Playwright fallback if basic requests are blocked

---

## 11. Deployment

| Component | Hackathon Demo | Production |
|---|---|---|
| Gemma 4 + Ollama | Local machine | Local machine |
| FastAPI backend | Local + ngrok tunnel | Render free tier |
| PostgreSQL + Redis | Docker Compose | Render / Supabase |
| Next.js frontend | Vercel preview deploy | Vercel production |

### Three commands to run everything locally:
```bash
ollama pull gemma4:4b
docker compose up
cd frontend && npm run dev
```

---

## 12. Build Priority Order

1. Get Gemma 4 returning clean JSON from a real LCPS chunk — **this is the critical unblock**
2. PDF extractor + chunker working on one real document
3. PostgreSQL schema initialized, models written, Alembic migrations run
4. Scraper finding real PDFs on lcps.org + Legistar API for Loudoun BOS
5. APScheduler running the full pipeline on a timer
6. FastAPI `/api/meetings` and `/api/categories` endpoints serving real data
7. Next.js frontend on Vercel showing real cards
8. WebSocket live update toast notification
9. Docker Compose — judges can run everything in one command
10. Demo video — real PDF in → Gemma 4 rewrites it → blog card on public URL
11. README complete
12. Kaggle Notebook technical write-up
13. Submit before May 18, 2026 at 11:59 PM UTC

---

## 13. Quality Metrics

| Metric | Target |
|---|---|
| Summary accuracy | Content matches actual agenda item — verified on 5 real documents |
| Category accuracy | Primary category correct for 90%+ of items |
| Mobile rendering | Fully usable on a 375px phone screen |
| Page load time | Meeting feed renders under 2 seconds |
| Pipeline reliability | Zero crashes on 3 consecutive nightly runs |

---

## 14. Out of Scope (v1.0)

- Multi-county support
- User accounts or personalization
- Email / push notification alerts
- Real-time live meeting processing
- Chatbot or Q&A interface
- OCR for scanned PDFs
- Native mobile app
- Celery task queue (APScheduler is sufficient)
