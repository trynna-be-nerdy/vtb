import { NextRequest, NextResponse } from 'next/server'
import { publishUpdate } from '@/lib/redis'

export const runtime = 'nodejs'

const PIPELINE_API_KEY = process.env.PIPELINE_API_KEY ?? 'change-me-in-production'

export async function POST(request: NextRequest) {
  const apiKey = request.headers.get('x-api-key')
  if (apiKey !== PIPELINE_API_KEY) {
    return NextResponse.json({ error: 'Invalid API key' }, { status: 403 })
  }

  // Publish trigger event and fire the runner as a background task.
  // The runner is imported dynamically to avoid bundling its heavy deps
  // (pdf-parse, etc.) in routes that don't need them.
  await publishUpdate({ event: 'pipeline_triggered' })

  // Fire-and-forget — runs after response is sent (Node.js runtime only).
  // On Vercel Pro/Enterprise, wrap in waitUntil instead.
  setImmediate(() => {
    import('@/lib/pipeline/runner')
      .then(({ runPipeline }) => runPipeline())
      .catch(err => console.error('[pipeline/trigger] runner error:', err))
  })

  return NextResponse.json({
    triggered: true,
    message: 'Pipeline run started. Check /api/health for status.',
  })
}
