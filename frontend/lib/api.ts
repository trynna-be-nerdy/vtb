/**
 * Client-side API functions for TanStack Query.
 * Used only in client components — imports from here trigger HTTP fetches.
 * Server components should import from lib/data.ts directly.
 */

import type { MeetingCard, MeetingListResponse, HealthResponse, SearchResponse } from './types'

// In the same Next.js app, API routes are relative. The browser resolves these.
// Server components use lib/data.ts directly to avoid HTTP round-trips.
const API_BASE = '/api'

// ── Server-side helpers (called from server components via lib/data.ts) ────────
// These remain for backward compatibility with any ISR fetch patterns.
// They use the absolute URL needed for server-side fetch() calls.

const INTERNAL_API =
  typeof window === 'undefined'
    ? (process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000') + '/api'
    : '/api'

export async function fetchBoardMeetings(
  board: string,
  limit = 3,
): Promise<MeetingCard[]> {
  try {
    const res = await fetch(
      `${INTERNAL_API}/meetings?board=${encodeURIComponent(board)}&limit=${limit}&page=1`,
      { next: { revalidate: 60 } },
    )
    if (!res.ok) return []
    const data: MeetingListResponse = await res.json()
    return data.meetings
  } catch {
    return []
  }
}

export async function fetchRecentMeetings(limit = 9): Promise<MeetingCard[]> {
  try {
    const res = await fetch(
      `${INTERNAL_API}/meetings?limit=${limit}&page=1`,
      { next: { revalidate: 60 } },
    )
    if (!res.ok) return []
    const data: MeetingListResponse = await res.json()
    return data.meetings
  } catch {
    return []
  }
}

export async function fetchHealth(): Promise<HealthResponse | null> {
  try {
    const res = await fetch(`${INTERNAL_API}/health`, { next: { revalidate: 60 } })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

// ── Client-side fetchers (used by TanStack Query hooks) ───────────────────────

export async function clientFetchBoardMeetings(
  board: string,
  limit = 3,
): Promise<MeetingCard[]> {
  const res = await fetch(
    `${API_BASE}/meetings?board=${encodeURIComponent(board)}&limit=${limit}&page=1`,
  )
  if (!res.ok) throw new Error(`Failed to fetch meetings for ${board}`)
  const data: MeetingListResponse = await res.json()
  return data.meetings
}

export async function clientSearch(q: string, page = 1): Promise<SearchResponse> {
  const res = await fetch(
    `${API_BASE}/search?q=${encodeURIComponent(q)}&page=${page}`,
  )
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}
