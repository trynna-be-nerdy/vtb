import { NextResponse } from 'next/server'
import { getHealth } from '@/lib/data'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET() {
  try {
    const data = await getHealth()
    return NextResponse.json(data)
  } catch (err) {
    console.error('/api/health error:', err)
    return NextResponse.json(
      { status: 'error', error: 'Internal server error' },
      { status: 500 },
    )
  }
}
