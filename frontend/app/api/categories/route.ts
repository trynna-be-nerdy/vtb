import { NextResponse } from 'next/server'
import { getCategories } from '@/lib/data'

export const runtime = 'nodejs'

export async function GET() {
  try {
    const data = await getCategories()
    return NextResponse.json(data)
  } catch (err) {
    console.error('/api/categories error:', err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
