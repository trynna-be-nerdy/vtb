/**
 * Ollama/Gemma client — direct port of backend/llm/ollama_client.py
 */

const OLLAMA_BASE_URL = process.env.OLLAMA_BASE_URL ?? 'http://localhost:11434'
const MODEL_NAME = process.env.OLLAMA_MODEL ?? 'gemma4:4b'
const MAX_RETRIES = 2

const RETRY_SUFFIX =
  '\n\nCRITICAL: Your previous response was not valid JSON or had missing fields. ' +
  'Return ONLY a raw JSON object — no markdown fences, no backticks, no explanatory text, ' +
  'nothing before or after the opening and closing braces.'

const PROMPT_1 = `You are a plain-English rewriter for government meeting documents.
Analyze the official government meeting text below and return ONLY a valid JSON object.
No markdown, no backticks, no explanation before or after the JSON.

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
{chunk}`

const PROMPT_2 = `You are a classifier for local government meeting content.
Analyze the meeting summary below and return ONLY a valid JSON object.
No markdown, no backticks, no text before or after the JSON.

The primary_category MUST be exactly one of these 12 slugs:
schools-education | school-construction | budget-finance | transportation |
zoning-land-use | public-safety | policy-governance | equity-inclusion |
technology | community-parks | personnel | general

Required JSON structure (all fields mandatory):
{
  "primary_category": "<one slug from the list above>",
  "secondary_tags": ["<specific sub-topic tag>"],
  "urgency": "<routine OR notable OR significant>",
  "fiscal_impact": <true or false>,
  "affects_schools": ["<school name if mentioned — empty array if none>"]
}

Meeting summary:
{summary}`

const PROMPT_3 = `You are a summarizer for local government meetings.
Review all agenda item summaries below from one meeting and return ONLY a valid JSON object.
No markdown, no backticks, no text before or after the JSON.

Required JSON structure (all fields mandatory):
{
  "meeting_overview": "<3-5 sentence overview of the entire meeting for a general audience>",
  "top_decisions": ["<1st most significant decision>", "<2nd>", "<3rd>"],
  "fiscal_total": "<total spending approved as a string like '$2.3M', or null if none>",
  "next_meeting_notes": "<scheduled follow-up items or next meeting info, or null if none>"
}

Agenda item summaries:
{summaries}`

const VALID_CATEGORIES = new Set([
  'schools-education', 'school-construction', 'budget-finance', 'transportation',
  'zoning-land-use', 'public-safety', 'policy-governance', 'equity-inclusion',
  'technology', 'community-parks', 'personnel', 'general',
])
const VALID_URGENCY = new Set(['routine', 'notable', 'significant'])

async function callOllama(prompt: string): Promise<string> {
  const resp = await fetch(`${OLLAMA_BASE_URL}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: MODEL_NAME, prompt, stream: false, format: 'json' }),
    signal: AbortSignal.timeout(600_000), // 10 min
  })
  if (!resp.ok) throw new Error(`Ollama HTTP ${resp.status}`)
  const body = (await resp.json()) as { response: string }
  return body.response
}

async function parseWithRetry<T>(prompt: string, validate: (raw: unknown) => T): Promise<T> {
  let lastError: unknown
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    const currentPrompt = attempt === 0 ? prompt : prompt + RETRY_SUFFIX
    try {
      const raw = await callOllama(currentPrompt)
      const data: unknown = JSON.parse(raw)
      return validate(data)
    } catch (err) {
      lastError = err
    }
  }
  throw new Error(`LLM failed after ${MAX_RETRIES + 1} attempts: ${lastError}`)
}

// ── Public API ─────────────────────────────────────────────────────────────────

export interface ContentRewriteResult {
  title: string
  summary: string
  decisions: string[]
  action_items: string[]
  key_figures: {
    amounts: string[]
    vote_tallies: string[]
    dates: string[]
    schools: string[]
  }
}

export interface ClassificationResult {
  primary_category: string
  secondary_tags: string[]
  urgency: string
  fiscal_impact: boolean
  affects_schools: string[]
}

export interface MeetingOverviewResult {
  meeting_overview: string
  top_decisions: string[]
  fiscal_total: string | null
  next_meeting_notes: string | null
}

export async function rewriteContent(chunk: string): Promise<ContentRewriteResult> {
  const prompt = PROMPT_1.replace('{chunk}', chunk)
  return parseWithRetry(prompt, (data) => {
    const d = data as Record<string, unknown>
    const title = String(d.title ?? '').split(' ').slice(0, 10).join(' ')
    return {
      title,
      summary: String(d.summary ?? ''),
      decisions: Array.isArray(d.decisions) ? (d.decisions as string[]) : [],
      action_items: Array.isArray(d.action_items) ? (d.action_items as string[]) : [],
      key_figures: {
        amounts: Array.isArray((d.key_figures as Record<string, unknown>)?.amounts) ? ((d.key_figures as Record<string, string[]>).amounts) : [],
        vote_tallies: Array.isArray((d.key_figures as Record<string, unknown>)?.vote_tallies) ? ((d.key_figures as Record<string, string[]>).vote_tallies) : [],
        dates: Array.isArray((d.key_figures as Record<string, unknown>)?.dates) ? ((d.key_figures as Record<string, string[]>).dates) : [],
        schools: Array.isArray((d.key_figures as Record<string, unknown>)?.schools) ? ((d.key_figures as Record<string, string[]>).schools) : [],
      },
    }
  })
}

export async function classifyContent(summary: string): Promise<ClassificationResult> {
  const prompt = PROMPT_2.replace('{summary}', summary)
  return parseWithRetry(prompt, (data) => {
    const d = data as Record<string, unknown>
    const category = String(d.primary_category ?? 'general')
    const urgency = String(d.urgency ?? 'routine').toLowerCase()
    return {
      primary_category: VALID_CATEGORIES.has(category) ? category : 'general',
      secondary_tags: Array.isArray(d.secondary_tags) ? (d.secondary_tags as string[]) : [],
      urgency: VALID_URGENCY.has(urgency) ? urgency : 'routine',
      fiscal_impact: Boolean(d.fiscal_impact),
      affects_schools: Array.isArray(d.affects_schools) ? (d.affects_schools as string[]) : [],
    }
  })
}

export async function generateMeetingOverview(summaries: string[]): Promise<MeetingOverviewResult> {
  const combined = summaries.join('\n\n---\n\n')
  const prompt = PROMPT_3.replace('{summaries}', combined)
  return parseWithRetry(prompt, (data) => {
    const d = data as Record<string, unknown>
    return {
      meeting_overview: String(d.meeting_overview ?? ''),
      top_decisions: (Array.isArray(d.top_decisions) ? (d.top_decisions as string[]) : []).slice(0, 3),
      fiscal_total: d.fiscal_total ? String(d.fiscal_total) : null,
      next_meeting_notes: d.next_meeting_notes ? String(d.next_meeting_notes) : null,
    }
  })
}
