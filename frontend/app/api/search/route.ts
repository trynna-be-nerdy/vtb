import { NextRequest, NextResponse } from 'next/server'
import { searchItems } from '@/lib/data'

export const runtime = 'nodejs'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const q = searchParams.get('q') ?? ''
    if (q.length < 2 || q.length > 200) {
      return NextResponse.json(
        { error: 'Query must be between 2 and 200 characters' },
        { status: 400 },
      )
    }

    const page = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10))
    const limit = Math.min(100, Math.max(1, parseInt(searchParams.get('limit') ?? '20', 10)))

    const data = await searchItems(q, page, limit)
    return NextResponse.json(data)
  } catch (err) {
    console.error('/api/search error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
