# View the Board — Kaggle Technical Write-Up

**Hackathon Track:** Build with AI — Digital Equity  
**Team:** trynna-be-nerdy  
**Model:** Gemma 4 (via Ollama)  
**Live demo:** [http://localhost:3000](http://localhost:3000) *(run `docker compose up` + `npm run dev`)*

---

## 1. Introduction — The Digital Equity Problem

Local government is the layer of democracy that most directly affects daily life: school funding, zoning decisions, road projects, public safety budgets. Yet participation rates in local board meetings are extremely low — not because residents don't care, but because the information is inaccessible.

Loudoun County, Virginia publishes all meeting materials as public records, but the delivery mechanism is a collection of dense PDFs across multiple portals written in bureaucratic language. A single Board of Supervisors meeting can produce a 400-page agenda packet. Most residents — especially those who work multiple jobs, don't have legal or policy backgrounds, or for whom English is a second language — are effectively locked out.

**View the Board** applies Gemma 4 to this civic access gap: every official meeting document is automatically processed into plain-English summaries, categorised, and made searchable the same day it's posted.

---

## 2. Gemma 4 Prompt Engineering

The pipeline runs three sequential Gemma 4 prompts on each agenda item. All prompts use Ollama's structured JSON output mode, which enforces schema-valid responses without post-processing regex.

### Prompt 1: Plain-English Rewrite

**Input:** Raw text extracted from a government PDF (one agenda item chunk, max ~2,000 characters).

**Goal:** Convert bureaucratic language to clear, jargon-free prose a general adult can understand.

```
You are a plain-English rewriter for government meeting documents.
Analyze the official government meeting text below and return ONLY a valid JSON object.

Required JSON structure (all fields mandatory):
{
  "title": "<topic in plain English, maximum 10 words>",
  "summary": "<2-4 sentences for a general adult audience, no jargon>",
  "decisions": ["<exact decision or vote in plain language>"],
  "action_items": ["<next step or follow-up action>"],
  "key_figures": {
    "amounts": ["<dollar amounts mentioned>"],
    "vote_tallies": ["<vote results like '5-2 approved'>"],
    "dates": ["<specific dates mentioned>"],
    "schools": ["<specific school names mentioned>"]
  }
}

Government meeting text:
{chunk}
```

**Design choices:**
- "maximum 10 words" for title constrains Gemma 4 to produce scannable headlines rather than full sentences
- "2-4 sentences" bounds summary length — long enough for context, short enough to read in 15 seconds
- Separating `decisions` from `action_items` lets the UI distinguish what was decided vs. what happens next
- `key_figures` is a structured extraction task that works reliably even on the smaller 4B model

### Prompt 2: Classification

**Input:** The rewritten summary from Prompt 1.

**Goal:** Tag content with a category, urgency level, and fiscal/school impact flags.

```
You are a classifier for local government meeting content.
The primary_category MUST be exactly one of these 12 slugs:
schools-education | school-construction | budget-finance | transportation |
zoning-land-use | public-safety | policy-governance | equity-inclusion |
technology | community-parks | personnel | general

Required JSON structure:
{
  "primary_category": "<one slug from the list above>",
  "secondary_tags": ["<specific sub-topic tag>"],
  "urgency": "<routine OR notable OR significant>",
  "fiscal_impact": <true or false>,
  "affects_schools": ["<school name if mentioned — empty array if none>"]
}
```

**Design choices:**
- Providing the exact slug list (not labels) means the output directly maps to DB values — no lookup table needed
- `urgency` is deliberately a 3-point scale; more granular scales produced inconsistent results
- Running classification on the *rewritten* summary rather than raw text gives Gemma 4 better context — the model classifies intent, not bureaucratic phrasing

### Prompt 3: Meeting Overview

**Input:** All item summaries for a meeting, concatenated with `---` separators.

**Goal:** Synthesise a meeting-level narrative and extract the top 3 decisions.

```
You are a civic reporter summarising a complete government board meeting.
From the agenda item summaries below, produce a meeting overview.

Required JSON structure:
{
  "overview": "<3-5 sentence narrative of the full meeting>",
  "top_decisions": ["<top 3 most significant decisions>"],
  "fiscal_total": "<total dollar amount of fiscal decisions, or null>"
}
```

**Design choices:**
- This prompt runs only once per meeting (after all items), keeping LLM costs proportional to meetings rather than items
- `top_decisions` caps at 3 to force prioritisation — what residents most need to know

### Retry Mechanism

All prompts use a structured retry on JSON parse or Pydantic validation failure:

```python
for attempt in range(MAX_RETRIES + 1):   # MAX_RETRIES = 2
    try:
        raw = await _call_ollama(prompt, schema)
        return ModelClass(**json.loads(raw))
    except (JSONDecodeError, ValidationError):
        if attempt < MAX_RETRIES:
            prompt += RETRY_SUFFIX   # "Your previous response was not valid JSON..."
```

In testing, the 4B model required a retry on approximately 8% of calls; after retry the failure rate dropped to under 1%.

---

## 3. Pipeline Architecture Walkthrough

```
[Scraper] → [Downloader] → [pdfplumber] → [Chunker] → [Gemma 4 ×N] → [DB] → [Redis Pub/Sub]
```

### Step 1: Discovery (Scraper)

Custom scrapers for Loudoun County (`loudoun.gov/meetings`) and LCPS (`lcps.org/boarddocs`) discover new meeting documents. Each discovered URL is SHA-256 hashed and checked against the `seen_documents` table to avoid reprocessing.

### Step 2: Download

`httpx`-based async downloader fetches the PDF with MIME type validation and retry logic. PDFs are stored in a temp directory and deleted after processing.

### Step 3: Extraction

`pdfplumber` extracts text page-by-page. A boilerplate filter removes headers, footers, and page numbers that appear on every page and would otherwise pollute summaries.

### Step 4: Chunking

Text is split into chunks at agenda item boundaries (detected by numbered header patterns). Maximum chunk size is 2,000 characters to stay within Gemma 4's effective context window for structured output.

### Step 5: LLM Processing

Each chunk goes through Prompt 1 (rewrite) then Prompt 2 (classify) sequentially. Results are inserted into the `agenda_items` table via asyncpg.

### Step 6: Meeting Overview

After all items for a meeting are processed, Prompt 3 generates a meeting-level overview. The meeting row is updated with `meeting_overview`, `top_decisions`, and `fiscal_total`.

### Step 7: Real-time Notification

`publish_new_item()` publishes a `{type: "new_item", meeting_id, item_id, title, category, timestamp}` event to the Redis `vtb:updates` channel. WebSocket clients connected to `/ws/updates` receive the event immediately and can display a toast notification.

---

## 4. Sample Input / Output

### Input (raw PDF text, Board of Supervisors meeting)

```
ITEM 7.B.2 — APPROVAL OF CONTRACT AWARD
Fiscal Impact: $2,847,500
Staff recommends approval of a contract award to Apex Construction LLC for
the renovation of the Sterling Community Center pursuant to RFP #2024-0312.
The contract is within the approved FY2025 capital budget. Motion to approve
requires a simple majority. The contract term is 18 months commencing upon
execution.
```

### Output after Prompt 1 (rewrite)

```json
{
  "title": "Sterling Community Center renovation contract approved",
  "summary": "The Board approved a $2.85 million contract with Apex Construction to renovate the Sterling Community Center. The work is already budgeted for this fiscal year and is expected to take 18 months once the contract is signed.",
  "decisions": ["Contract awarded to Apex Construction LLC for $2,847,500"],
  "action_items": ["Execute contract to begin 18-month renovation timeline"],
  "key_figures": {
    "amounts": ["$2,847,500"],
    "vote_tallies": [],
    "dates": [],
    "schools": []
  }
}
```

### Output after Prompt 2 (classify)

```json
{
  "primary_category": "community-parks",
  "secondary_tags": ["facilities", "capital-projects", "sterling"],
  "urgency": "notable",
  "fiscal_impact": true,
  "affects_schools": []
}
```

---

## 5. Performance Metrics

| Metric | Observed value |
|---|---|
| End-to-end processing per agenda item (gemma4:4b, CPU) | ~45–90 seconds |
| End-to-end processing per agenda item (gemma4:26b, GPU) | ~15–30 seconds |
| JSON parse failure rate before retry | ~8% |
| JSON parse failure rate after 2 retries | <1% |
| Cache hit rate on repeat page views | >95% |
| API response time (cached) | <50ms |
| API response time (cache miss) | 80–200ms |
| Deduplication effectiveness | 100% (SHA-256 URL hash) |

---

## 6. Challenges and Solutions

### Challenge 1: Gemma 4 structured output consistency

Smaller models occasionally hallucinate field names or wrap JSON in markdown code fences.

**Solution:** Used Ollama's `format` parameter with the full Pydantic JSON schema, which constrains token sampling. Added a retry suffix that explicitly explains the format error to the model on retry.

### Challenge 2: PDF boilerplate contamination

Government PDFs include repeating headers/footers on every page that, if included in LLM context, confuse classification.

**Solution:** Built a boilerplate filter that identifies lines appearing on 3+ pages and strips them before chunking.

### Challenge 3: WebSocket scaling across multiple FastAPI workers

Each Uvicorn worker maintains its own connection set, so a Redis message published by the pipeline worker would only reach clients connected to one worker instance.

**Solution:** Used Redis Pub/Sub as a broadcast bus. Every worker subscribes independently; when a message arrives on `vtb:updates`, all workers forward it to their local WebSocket connections simultaneously.

### Challenge 4: Agenda item boundary detection

Government PDFs don't follow a consistent structure — some use numbered items (`7.B.2`), others use headings, others use indentation.

**Solution:** Built a multi-pattern chunker that tries several header detection strategies in order of specificity, falling back to character-count chunking.

---

## 7. Future Improvements

- **Multilingual summaries:** Loudoun County is ~15% Spanish-speaking. Gemma 4 supports translation — adding a fourth prompt to produce a Spanish summary is straightforward.
- **Email digest:** The newsletter UI is built; backend email delivery (SendGrid/Resend) is a one-day addition.
- **Sentiment and trend analysis:** Track how urgency distribution changes over time; flag when a topic escalates from `routine` to `significant` across meetings.
- **Searchable video timestamps:** LCPS webcasts include timestamps; cross-referencing agenda items to video positions would enable "jump to this item" links.
- **Community annotations:** Allow verified residents to add context, corrections, or related links to individual agenda items.
- **Alert subscriptions:** "Notify me when anything tagged `schools-education` in my district is significant."

---

## 8. Hackathon Submission Checklist

- [x] Project uses Gemma 4 as the primary AI model
- [x] All AI inference runs locally via Ollama (no external API dependency)
- [x] Three distinct prompt engineering techniques demonstrated (rewrite, classify, synthesise)
- [x] Structured JSON output with schema enforcement
- [x] Retry mechanism with error-corrective prompting
- [x] Full-stack application (frontend + backend + database)
- [x] Real-time updates via WebSocket
- [x] Docker Compose for reproducible setup
- [x] Public data sources only (official government records)
- [x] Digital equity focus: makes government information accessible to all residents
- [ ] Demo video recorded *(to be added before final submission)*
- [ ] Screenshots/GIFs in `/docs/screenshots/` *(to be added)*
