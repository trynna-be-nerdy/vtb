import { createHash } from 'crypto'

export interface DocumentInfo {
  url: string
  pdf_url: string
  title: string
  meeting_date: string // YYYY-MM-DD
  board_type: string   // board-of-supervisors | planning-commission | lcps-school-board | advisory-boards
  sha256?: string
}

export function sha256(content: Buffer): string {
  return createHash('sha256').update(content).digest('hex')
}

export const BROWSER_HEADERS: Record<string, string> = {
  'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.9',
}

export const JSON_HEADERS: Record<string, string> = {
  ...BROWSER_HEADERS,
  Accept: 'application/json, text/plain, */*',
}

export const RATE_LIMIT_MS = 4_000
