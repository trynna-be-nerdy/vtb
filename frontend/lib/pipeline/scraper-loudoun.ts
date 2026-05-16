/**
 * Loudoun County scraper using the Legistar JSON API.
 * Port of backend/pipeline/scrapers/loudoun_scraper.py
 */

import type { DocumentInfo } from './types'
import { JSON_HEADERS, RATE_LIMIT_MS } from './types'

const API_BASE = 'https://webapi.legistar.com/v1/loudouncounty'
const RECENT_EVENTS = 50

const BOARD_TYPE_MAP: Array<[string, string]> = [
  ['supervisor', 'board-of-supervisors'],
  ['planning',   'planning-commission'],
  ['advisory',   'advisory-boards'],
]

function mapBoardType(bodyName: string): string {
  const lower = bodyName.toLowerCase()
  for (const [fragment, slug] of BOARD_TYPE_MAP) {
    if (lower.includes(fragment)) return slug
  }
  return 'advisory-boards'
}

function parseLegistarDate(raw: string): string | null {
  if (!raw) return null
  const match = raw.match(/^(\d{4}-\d{2}-\d{2})/)
  return match ? match[1] : null
}

let lastRequestTime = 0

async function rateLimitedFetch(url: string): Promise<unknown> {
  const now = Date.now()
  const wait = RATE_LIMIT_MS - (now - lastRequestTime)
  if (wait > 0) await new Promise(r => setTimeout(r, wait))

  const resp = await fetch(url, { headers: JSON_HEADERS })
  lastRequestTime = Date.now()
  if (!resp.ok) throw new Error(`Legistar HTTP ${resp.status}: ${url}`)
  return resp.json()
}

async function findAgendaAttachment(eventId: number): Promise<string | null> {
  try {
    const url = `${API_BASE}/events/${eventId}/eventitems?$expand=EventItemAttachments`
    const items = (await rateLimitedFetch(url)) as Array<Record<string, unknown>>
    for (const item of items) {
      const attachments = (item.EventItemAttachments as Array<Record<string, string>>) ?? []
      for (const att of attachments) {
        const href = att.MatterAttachmentHyperlink ?? ''
        if (href.toLowerCase().endsWith('.pdf')) return href
      }
    }
  } catch {
    // ignore
  }
  return null
}

export async function discoverLoudounDocuments(): Promise<DocumentInfo[]> {
  const url =
    `${API_BASE}/events` +
    `?$top=${RECENT_EVENTS}` +
    `&$orderby=EventDate desc` +
    `&$filter=EventAgendaStatusName eq 'Final'`

  const events = (await rateLimitedFetch(url)) as Array<Record<string, unknown>>
  const docs: DocumentInfo[] = []

  for (const event of events) {
    try {
      const eventId = event.EventId as number | undefined
      if (!eventId) continue

      const rawDate = String(event.EventDate ?? '')
      const meeting_date = parseLegistarDate(rawDate)
      if (!meeting_date) continue

      const bodyName = String(event.EventBodyName ?? '')
      const board_type = mapBoardType(bodyName)
      const title = `${bodyName} – ${meeting_date}`

      let pdf_url = (event.EventAgendaFile ?? event.EventMinutesFile ?? '') as string
      if (!pdf_url) {
        const found = await findAgendaAttachment(eventId)
        if (found) pdf_url = found
      }
      if (!pdf_url) continue

      if (!pdf_url.startsWith('http')) {
        pdf_url = `https://loudoun.legistar.com${pdf_url}`
      }

      const landing_url =
        (event.EventInSiteURL as string) ??
        `https://loudoun.legistar.com/MeetingDetail.aspx?ID=${eventId}`

      docs.push({ url: landing_url, pdf_url, title, meeting_date, board_type })
    } catch {
      // skip malformed events
    }
  }

  return docs
}
