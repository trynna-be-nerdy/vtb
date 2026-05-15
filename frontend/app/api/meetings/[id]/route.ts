import { NextRequest, NextResponse } from 'next/server'
import { getMeeting } from '@/lib/data'

export const runtime = 'nodejs'

export async function GET(
  _request: NextRequest,
  { params }: { params: { id: string } },
) {
  try {
    const id = parseInt(params.id, 10)
    if (isNaN(id)) {
      return NextResponse.json({ error: 'Invalid meeting ID' }, { status: 400 })
    }

    const data = await getMeeting(id)
    if (!data) {
      return NextResponse.json({ error: 'Meeting not found' }, { status: 404 })
    }

    return NextResponse.json(data)
  } catch (err) {
    console.error(`/api/meetings/${params.id} error:`, err)
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 })
  }
}
