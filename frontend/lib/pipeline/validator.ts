/**
 * Quality validator for agenda items produced by the LLM pipeline.
 * Mirrors the 10-check spec from task 5.
 * Call before insertAgendaItem; skip the item (don't crash the document) on failure.
 */

export interface AgendaItemDraft {
  title: string
  summary: string
  decisions: string[]
  primary_category: string
  urgency: string
  key_figures: {
    amounts: string[]
    vote_tallies: string[]
    dates?: string[]
    schools?: string[]
  }
  source_pdf_url: string
}

export interface ValidationResult {
  valid: boolean
  errors: string[]
}

const VALID_CATEGORIES = new Set([
  'schools-education', 'school-construction', 'budget-finance', 'transportation',
  'zoning-land-use', 'public-safety', 'policy-governance', 'equity-inclusion',
  'technology', 'community-parks', 'personnel', 'general',
])

const VALID_URGENCY = new Set(['routine', 'notable', 'significant'])

// $1M | $2.3M | $450K | $4,800,000 | $1.2B (case-insensitive suffix)
const CURRENCY_RE = /^\$[\d,]+(\.\d+)?[KMBkmb]?$/

// 5-2 | 6–1 | 4-3-0 | 7-0 (supports en-dash and three-way splits)
const VOTE_TALLY_RE = /^\d+[-–]\d+([-–]\d+)?$/

const URL_RE = /^https?:\/\/.+/

/**
 * Validate one agenda item draft before writing to the DB.
 *
 * @param item           The draft produced by the LLM
 * @param seenTitles     Mutable set of normalised titles already accepted in this meeting.
 *                       Pass the same Set instance across all items for one document so
 *                       check #8 (no duplicates within a meeting) works correctly.
 */
export function validateAgendaItem(
  item: AgendaItemDraft,
  seenTitles: Set<string>,
): ValidationResult {
  const errors: string[] = []

  // 1. Title not empty, under 100 chars
  const trimmedTitle = item.title?.trim() ?? ''
  if (trimmedTitle.length === 0) {
    errors.push('Title is empty')
  } else if (trimmedTitle.length > 100) {
    errors.push(`Title too long: ${trimmedTitle.length} chars (max 100)`)
  }

  // 2. Summary between 50 and 500 chars
  const summaryLen = item.summary?.trim().length ?? 0
  if (summaryLen < 50) {
    errors.push(`Summary too short: ${summaryLen} chars (min 50)`)
  } else if (summaryLen > 500) {
    errors.push(`Summary too long: ${summaryLen} chars (max 500)`)
  }

  // 3. primary_category must be one of the 12 valid slugs
  if (!VALID_CATEGORIES.has(item.primary_category)) {
    errors.push(`Invalid primary_category: "${item.primary_category}"`)
  }

  // 4. urgency must be routine | notable | significant
  if (!VALID_URGENCY.has(item.urgency?.toLowerCase())) {
    errors.push(`Invalid urgency: "${item.urgency}"`)
  }

  // 5. Non-routine items must have at least one decision
  if (item.urgency !== 'routine' && (item.decisions?.length ?? 0) === 0) {
    errors.push(`Non-routine item (urgency="${item.urgency}") has no decisions`)
  }

  // 6. Dollar amounts must look like currency strings
  for (const amount of item.key_figures.amounts ?? []) {
    const s = amount?.trim()
    if (s && !CURRENCY_RE.test(s)) {
      errors.push(`Invalid currency amount: "${s}"`)
    }
  }

  // 7. Vote tallies must match N-N or N-N-N pattern
  for (const tally of item.key_figures.vote_tallies ?? []) {
    const s = tally?.trim()
    if (s && !VOTE_TALLY_RE.test(s)) {
      errors.push(`Invalid vote tally: "${s}"`)
    }
  }

  // 8. No duplicate titles within the same meeting
  const normTitle = trimmedTitle.toLowerCase()
  if (normTitle && seenTitles.has(normTitle)) {
    errors.push(`Duplicate agenda item title in this meeting: "${trimmedTitle}"`)
  } else if (normTitle) {
    seenTitles.add(normTitle)
  }

  // 9. Page range — the current chunker splits on header patterns, not page boundaries,
  //    so no page-range metadata is tracked. This check is a no-op and documented here
  //    so it can be enabled if the extractor gains per-page tracking in the future.

  // 10. Source PDF URL must be a valid http(s) URL
  if (!URL_RE.test(item.source_pdf_url ?? '')) {
    errors.push(`Invalid source_pdf_url: "${item.source_pdf_url}"`)
  }

  return { valid: errors.length === 0, errors }
}
