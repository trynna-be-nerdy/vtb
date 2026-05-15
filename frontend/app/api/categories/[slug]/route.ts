import { NextRequest, NextResponse } from 'next/server'
import { getCategoryFeed } from '@/lib/data'

export const runtime = 'nodejs'

export async function GET(
  request: NextRequest,
  { params }: { params: { slug: string } },
) {
  try {
    const { searchParams } = new URL(request.url)
    const page = Math.max(1, parseInt(searchParams.get('page') ?? '1', 10))
    const limit = Math.min(100, Math.max(1, parseInt(searchParams.get('limit') ?? '20', 10)))

    const data = await getCategoryFeed(params.slug, page, limit)
    if (!data) {
      return NextResponse.json({ error: `Unknown category: ${params.slug}` }, { status: 404 })
    }

    return NextResponse.json(data)
  } catch (err) {
    console.error(`/api/categories/${params.slug} error:`, err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
