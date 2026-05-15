import { NextRequest, NextResponse } from 'next/server'
import { getMeetings } from '@/lib/data'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const board = searchParams.get('board') || null
    const page = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10))
    const limit = Math.min(100, Math.max(1, parseInt(searchParams.get('limit') ?? '20', 10)))

    const data = await getMeetings(board, page, limit)
    return NextResponse.json(data)
  } catch (err) {
    console.error('/api/meetings error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
