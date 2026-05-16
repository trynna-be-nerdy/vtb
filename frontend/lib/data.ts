/**
 * Server-side data access layer.
 * Import directly from server components and API route handlers.
 * Never import from client components.
 */
import { sql, serializeRow, serializeRows } from './db'
import { cacheGet, cacheSet, CACHE_TTL, SEARCH_TTL, HEALTH_TTL } from './redis'

// ── Category constants ────────────────────────────────────────────────────────

export const CATEGORY_LABELS: Record<string, string> = {
  'schools-education': 'Schools & Education',
  'school-construction': 'School Construction',
  'budget-finance': 'Budget & Finance',
  transportation: 'Transportation',
  'zoning-land-use': 'Zoning & Land Use',
  'public-safety': 'Public Safety',
  'policy-governance': 'Policy & Governance',
  'equity-inclusion': 'Equity & Inclusion',
  technology: 'Technology',
  'community-parks': 'Community & Parks',
  personnel: 'Personnel',
  general: 'General',
}

const ALL_CATEGORY_SLUGS = Object.keys(CATEGORY_LABELS)

// ── Meetings ──────────────────────────────────────────────────────────────────

export async function getMeetings(board: string | null, page: number, limit: number) {
  const cacheKey = `meetings:list:p=${page}:l=${limit}:b=${board}`
  const cached = await cacheGet(cacheKey)
  if (cached) return cached

  const offset = (page - 1) * limit

  const [countRows, rows] = await Promise.all([
    board
      ? sql`SELECT COUNT(*)::int AS total FROM meetings WHERE processing_status = 'completed' AND board_slug = ${board}`
      : sql`SELECT COUNT(*)::int AS total FROM meetings WHERE processing_status = 'completed'`,
    board
      ? sql`
          SELECT id, title, board_slug, meeting_date, meeting_overview,
                 top_decisions, fiscal_total, total_items, fiscal_items, processing_status
          FROM meetings
          WHERE processing_status = 'completed' AND board_slug = ${board}
          ORDER BY meeting_date DESC
          LIMIT ${limit} OFFSET ${offset}`
      : sql`
          SELECT id, title, board_slug, meeting_date, meeting_overview,
                 top_decisions, fiscal_total, total_items, fiscal_items, processing_status
          FROM meetings
          WHERE processing_status = 'completed'
          ORDER BY meeting_date DESC
          LIMIT ${limit} OFFSET ${offset}`,
  ])

  const total: number = countRows[0].total
  const payload = {
    meetings: serializeRows(rows as Record<string, unknown>[]),
    pagination: { page, limit, total, has_next: page * limit < total },
  }

  await cacheSet(cacheKey, payload)
  return payload
}

export async function getMeeting(id: number) {
  const cacheKey = `meetings:detail:${id}`
  const cached = await cacheGet(cacheKey)
  if (cached) return cached

  const [meetingRows, itemRows, docRows] = await Promise.all([
    sql`
      SELECT id, title, board_slug, meeting_date, source_url, source_pdf_url,
             meeting_overview, top_decisions, fiscal_total, next_meeting_notes,
             total_items, fiscal_items, processing_status, created_at, updated_at
      FROM meetings WHERE id = ${id}`,
    sql`
      SELECT id, meeting_id, title, summary, decisions, action_items, key_figures,
             primary_category, secondary_tags, urgency, fiscal_impact, affects_schools,
             source_pdf_url, page_range, created_at
      FROM agenda_items WHERE meeting_id = ${id} ORDER BY id`,
    sql`
      SELECT id, meeting_id, title, url, doc_type, created_at
      FROM supporting_documents WHERE meeting_id = ${id}`,
  ])

  if (meetingRows.length === 0) return null

  const meeting = serializeRow(meetingRows[0] as Record<string, unknown>)
  const payload = {
    meeting: {
      ...meeting,
      agenda_items: serializeRows(itemRows as Record<string, unknown>[]),
      supporting_documents: serializeRows(docRows as Record<string, unknown>[]),
    },
  }

  await cacheSet(cacheKey, payload)
  return payload
}

// ── Categories ────────────────────────────────────────────────────────────────

export async function getCategories() {
  const cacheKey = 'categories:all'
  const cached = await cacheGet(cacheKey)
  if (cached) return cached

  const rows = await sql`
    SELECT primary_category AS slug, COUNT(*)::int AS item_count
    FROM agenda_items
    GROUP BY primary_category`

  const counts: Record<string, number> = Object.fromEntries(ALL_CATEGORY_SLUGS.map(s => [s, 0]))
  for (const row of rows) {
    if (row.slug in counts) counts[row.slug as string] = row.item_count as number
  }

  const payload = {
    categories: ALL_CATEGORY_SLUGS.map(slug => ({
      slug,
      label: CATEGORY_LABELS[slug],
      item_count: counts[slug],
    })),
  }

  await cacheSet(cacheKey, payload, CACHE_TTL)
  return payload
}

export async function getCategoryFeed(slug: string, page: number, limit: number) {
  if (!(slug in CATEGORY_LABELS)) return null

  const cacheKey = `categories:feed:${slug}:p=${page}:l=${limit}`
  const cached = await cacheGet(cacheKey)
  if (cached) return cached

  const offset = (page - 1) * limit

  const [countRows, rows] = await Promise.all([
    sql`SELECT COUNT(*)::int AS total FROM agenda_items WHERE primary_category = ${slug}`,
    sql`
      SELECT id, meeting_id, title, summary, primary_category, secondary_tags, urgency,
             fiscal_impact, affects_schools, source_pdf_url, page_range, created_at
      FROM agenda_items
      WHERE primary_category = ${slug}
      ORDER BY created_at DESC
      LIMIT ${limit} OFFSET ${offset}`,
  ])

  const total: number = countRows[0].total
  const payload = {
    slug,
    label: CATEGORY_LABELS[slug],
    items: serializeRows(rows as Record<string, unknown>[]),
    pagination: { page, limit, total, has_next: page * limit < total },
  }

  await cacheSet(cacheKey, payload)
  return payload
}

// ── Calendar ──────────────────────────────────────────────────────────────────

export async function getMeetingsByMonth(year: number, month: number, board?: string | null) {
  // month is 1-based (1 = January)
  const pad = (n: number) => String(n).padStart(2, '0')
  const firstDay = `${year}-${pad(month)}-01`
  // Last day: day 0 of the next month
  const lastDayDate = new Date(year, month, 0)
  const lastDay = `${year}-${pad(month)}-${pad(lastDayDate.getDate())}`

  const cacheKey = `meetings:calendar:${year}-${pad(month)}:b=${board ?? 'all'}`
  const cached = await cacheGet(cacheKey)
  if (cached) return cached as { meetings: MeetingCalendarItem[] }

  const rows = board
    ? await sql`
        SELECT id, title, board_slug, meeting_date, processing_status, total_items
        FROM meetings
        WHERE meeting_date >= ${firstDay} AND meeting_date <= ${lastDay}
          AND board_slug = ${board}
        ORDER BY meeting_date ASC`
    : await sql`
        SELECT id, title, board_slug, meeting_date, processing_status, total_items
        FROM meetings
        WHERE meeting_date >= ${firstDay} AND meeting_date <= ${lastDay}
        ORDER BY meeting_date ASC`

  const payload = { meetings: serializeRows(rows as Record<string, unknown>[]) as unknown as MeetingCalendarItem[] }
  await cacheSet(cacheKey, payload, CACHE_TTL)
  return payload
}

export interface MeetingCalendarItem {
  id: number
  title: string
  board_slug: string
  meeting_date: string
  processing_status: string
  total_items: number
}

// ── Search ────────────────────────────────────────────────────────────────────

export async function searchItems(q: string, page: number, limit: number) {
  const cacheKey = `search:${q}:p=${page}:l=${limit}`
  const cached = await cacheGet(cacheKey)
  if (cached) return cached

  const offset = (page - 1) * limit

  const [countRows, rows] = await Promise.all([
    sql`
      SELECT COUNT(*)::int AS total FROM agenda_items
      WHERE search_vector @@ plainto_tsquery('english', ${q})`,
    sql`
      SELECT
        ai.id, ai.meeting_id, ai.title, ai.summary, ai.primary_category,
        ai.secondary_tags, ai.urgency, ai.fiscal_impact, ai.affects_schools,
        ai.source_pdf_url, ai.page_range, ai.created_at,
        m.title AS meeting_title,
        m.meeting_date,
        m.board_slug,
        ts_rank(ai.search_vector, plainto_tsquery('english', ${q})) AS rank
      FROM agenda_items ai
      JOIN meetings m ON ai.meeting_id = m.id
      WHERE ai.search_vector @@ plainto_tsquery('english', ${q})
      ORDER BY rank DESC
      LIMIT ${limit} OFFSET ${offset}`,
  ])

  const total: number = countRows[0].total
  const payload = {
    query: q,
    results: serializeRows(rows as Record<string, unknown>[]),
    pagination: { page, limit, total, has_next: page * limit < total },
  }

  await cacheSet(cacheKey, payload, SEARCH_TTL)
  return payload
}

// ── Health ────────────────────────────────────────────────────────────────────

export async function getHealth() {
  const cacheKey = 'health:status'
  const cached = await cacheGet(cacheKey)
  if (cached) return cached

  const now = new Date()
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString()

  const [lastRunRows, itemCountRows, queueRows] = await Promise.all([
    sql`SELECT started_at, finished_at, status FROM pipeline_runs ORDER BY started_at DESC LIMIT 1`,
    sql`SELECT COUNT(*)::int AS cnt FROM agenda_items WHERE created_at >= ${monthStart}`,
    sql`SELECT COUNT(*)::int AS cnt FROM seen_documents WHERE status IN ('pending', 'processing')`,
  ])

  const lastRun = lastRunRows[0] ?? null
  const payload = {
    status: 'ok',
    last_pipeline_run: lastRun ? (lastRun.started_at instanceof Date ? lastRun.started_at.toISOString() : lastRun.started_at) : null,
    last_pipeline_status: lastRun?.status ?? null,
    items_this_month: itemCountRows[0].cnt as number,
    queue_depth: queueRows[0].cnt as number,
  }

  await cacheSet(cacheKey, payload, HEALTH_TTL)
  return payload
}

// ── Pipeline runs (write) ─────────────────────────────────────────────────────

export async function createPipelineRun(): Promise<number> {
  const rows = await sql`
    INSERT INTO pipeline_runs (status, documents_found, documents_processed, items_created)
    VALUES ('running', 0, 0, 0)
    RETURNING id`
  return rows[0].id as number
}

export async function updatePipelineRun(
  id: number,
  update: {
    status: string
    documents_found?: number
    documents_processed?: number
    items_created?: number
    error_message?: string
  },
): Promise<void> {
  await sql`
    UPDATE pipeline_runs SET
      status = ${update.status},
      finished_at = NOW(),
      documents_found = COALESCE(${update.documents_found ?? null}, documents_found),
      documents_processed = COALESCE(${update.documents_processed ?? null}, documents_processed),
      items_created = COALESCE(${update.items_created ?? null}, items_created),
      error_message = COALESCE(${update.error_message ?? null}, error_message)
    WHERE id = ${id}`
}

// ── Seen documents (deduplication, write) ─────────────────────────────────────

export async function filterNewDocumentUrls(pdfUrls: string[]): Promise<Set<string>> {
  if (pdfUrls.length === 0) return new Set()
  const rows = await sql`
    SELECT url FROM seen_documents
    WHERE url = ANY(${pdfUrls}) AND status = 'completed'`
  return new Set(rows.map(r => r.url as string))
}

export async function upsertSeenDocument(
  url: string,
  sha256: string,
  status: 'pending' | 'processing' | 'completed' | 'failed',
): Promise<void> {
  await sql`
    INSERT INTO seen_documents (url, sha256, status)
    VALUES (${url}, ${sha256}, ${status})
    ON CONFLICT (url) DO UPDATE SET sha256 = EXCLUDED.sha256, status = EXCLUDED.status,
      updated_at = NOW()`
}

// ── Meetings & agenda items (write) ───────────────────────────────────────────

export async function upsertMeeting(m: {
  title: string
  board_slug: string
  meeting_date: string
  source_url?: string
  source_pdf_url?: string
}): Promise<number> {
  const rows = await sql`
    INSERT INTO meetings (title, board_slug, meeting_date, source_url, source_pdf_url,
                          processing_status, total_items, fiscal_items)
    VALUES (${m.title}, ${m.board_slug}, ${m.meeting_date},
            ${m.source_url ?? null}, ${m.source_pdf_url ?? null}, 'processing', 0, 0)
    ON CONFLICT DO NOTHING
    RETURNING id`

  if (rows.length > 0) return rows[0].id as number

  // Already exists — return existing id
  const existing = await sql`
    SELECT id FROM meetings WHERE board_slug = ${m.board_slug} AND meeting_date = ${m.meeting_date}`
  return existing[0].id as number
}

export async function insertAgendaItem(item: {
  meeting_id: number
  title: string
  summary: string
  decisions: string[]
  action_items: string[]
  key_figures: Record<string, unknown>
  primary_category: string
  secondary_tags: string[]
  urgency: string
  fiscal_impact: boolean
  affects_schools: string[]
  source_pdf_url?: string
  page_range?: string
}): Promise<number> {
  const rows = await sql`
    INSERT INTO agenda_items (
      meeting_id, title, summary, decisions, action_items, key_figures,
      primary_category, secondary_tags, urgency, fiscal_impact, affects_schools,
      source_pdf_url, page_range
    ) VALUES (
      ${item.meeting_id}, ${item.title}, ${item.summary},
      ${sql.array(item.decisions)}, ${sql.array(item.action_items)},
      ${sql.json(item.key_figures as Parameters<typeof sql.json>[0])},
      ${item.primary_category}, ${sql.array(item.secondary_tags)},
      ${item.urgency}, ${item.fiscal_impact}, ${sql.array(item.affects_schools)},
      ${item.source_pdf_url ?? null}, ${item.page_range ?? null}
    ) RETURNING id`
  return rows[0].id as number
}

export async function finalizeMeeting(
  meetingId: number,
  overview: {
    meeting_overview: string
    top_decisions: string[]
    fiscal_total: string | null
    next_meeting_notes: string | null
  },
  counts: { total_items: number; fiscal_items: number },
): Promise<void> {
  await sql`
    UPDATE meetings SET
      meeting_overview = ${overview.meeting_overview},
      top_decisions = ${sql.array(overview.top_decisions)},
      fiscal_total = ${overview.fiscal_total},
      next_meeting_notes = ${overview.next_meeting_notes},
      total_items = ${counts.total_items},
      fiscal_items = ${counts.fiscal_items},
      processing_status = 'completed',
      updated_at = NOW()
    WHERE id = ${meetingId}`
}
