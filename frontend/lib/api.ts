import type { MeetingCard, MeetingListResponse, HealthResponse } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export async function fetchBoardMeetings(
  board: string,
  limit = 3,
): Promise<MeetingCard[]> {
  try {
    const res = await fetch(
      `${API_URL}/api/meetings?board=${encodeURIComponent(board)}&limit=${limit}&page=1`,
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
      `${API_URL}/api/meetings?limit=${limit}&page=1`,
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
    const res = await fetch(`${API_URL}/api/health`, {
      next: { revalidate: 60 },
    })
    if (!res.ok) return null
    return res.json()
  } catch {
    return null
  }
}

// Client-side fetchers (no next cache option — used with TanStack Query)
export async function clientFetchBoardMeetings(
  board: string,
  limit = 3,
): Promise<MeetingCard[]> {
  const res = await fetch(
    `${API_URL}/api/meetings?board=${encodeURIComponent(board)}&limit=${limit}&page=1`,
  )
  if (!res.ok) throw new Error(`Failed to fetch meetings for ${board}`)
  const data: MeetingListResponse = await res.json()
  return data.meetings
}
