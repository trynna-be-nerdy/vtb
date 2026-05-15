/**
 * LCPS BoardDocs scraper.
 * Port of backend/pipeline/scrapers/lcps_scraper.py
 */

import type { DocumentInfo } from './types'
import { BROWSER_HEADERS, JSON_HEADERS, RATE_LIMIT_MS } from './types'

const BOARDDOCS_BASE = 'https://go.boarddocs.com/va/lcps/Board.nsf'
const MEETINGS_URL = `${BOARDDOCS_BASE}/getmeetings?open`
const AGENDA_URL = `${BOARDDOCS_BASE}/getAgenda?open`
const PDF_RE = /\/va\/lcps\/Board\.nsf\/files\/[^"']+\.pdf/i

let lastRequestTime = 0

async function rateLimitedFetch(url: string, json = false): Promise<Response> {
  const now = Date.now()
  const wait = RATE_LIMIT_MS - (now - lastRequestTime)
  if (wait > 0) await new Promise(r => setTimeout(r, wait))

  const resp = await fetch(url, { headers: json ? JSON_HEADERS : BROWSER_HEADERS })
  lastRequestTime = Date.now()
  if (!resp.ok) throw new Error(`BoardDocs HTTP ${resp.status}: ${url}`)
  return resp
}

function parseBoardDocsDate(raw: string | number): string | null {
  if (!raw) return null
  const s = String(raw).trim()
  // MM/DD/YYYY
  const mmddyyyy = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/)
  if (mmddyyyy) {
    const [, m, d, y] = mmddyyyy
    return `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`
  }
  // YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s
  // epoch ms
  const epochMs = parseInt(s, 10)
  if (!isNaN(epochMs) && epochMs > 1e10) {
    return new Date(epochMs).toISOString().split('T')[0]
  }
  return null
}

function extractPdfUrl(html: string): string | null {
  const match = PDF_RE.exec(html)
  if (match) return `https://go.boarddocs.com${match[0]}`

  // Simple link extraction without cheerio
  const linkRe = /href=["']([^"']*\.pdf)["']/gi
  let m: RegExpExecArray | null
  while ((m = linkRe.exec(html)) !== null) {
    const href = m[1]
    if (href.startsWith('http')) return href
    return `https://go.boarddocs.com${href}`
  }
  return null
}

export async function discoverLcpsDocuments(): Promise<DocumentInfo[]> {
  let meetings: Array<Record<string, unknown>>
  try {
    const resp = await rateLimitedFetch(MEETINGS_URL, true)
    const data: unknown = await resp.json()
    meetings = Array.isArray(data)
      ? (data as Array<Record<string, unknown>>)
      : ((data as Record<string, unknown>).meetings as Array<Record<string, unknown>>) ?? []
  } catch (err) {
    console.warn(`[lcps-scraper] BoardDocs meetings fetch failed: ${err}`)
    return []
  }

  const docs: DocumentInfo[] = []

  for (const meeting of meetings) {
    try {
      const unique = (meeting.unique ?? meeting.id) as string | undefined
      if (!unique) continue

      const rawDate = (meeting.date ?? meeting.startDate ?? '') as string
      const meeting_date = parseBoardDocsDate(rawDate)
      if (!meeting_date) continue

      const title =
        (meeting.name ?? meeting.title ?? `LCPS Meeting ${rawDate}`) as string

      let pdf_url: string | null = null
      try {
        const agendaResp = await rateLimitedFetch(`${AGENDA_URL}&id=${unique}`)
        pdf_url = extractPdfUrl(await agendaResp.text())
      } catch {
        // use landing page as best-guess
      }

      if (!pdf_url) {
        pdf_url = `${BOARDDOCS_BASE}/Public/${unique}?open`
      }

      docs.push({
        url: `${BOARDDOCS_BASE}/Public/${unique}?open`,
        pdf_url,
        title,
        meeting_date,
        board_type: 'lcps',
      })
    } catch {
      // skip
    }
  }

  return docs
}
