// Vercel cron-triggered pipeline endpoint.
// Replaces the Python APScheduler worker (backend/pipeline/worker.py).
// Schedule (vercel.json): "0 * /6 * * *" (every 6 hours) — the slash is split
// here only to avoid the */ sequence terminating this comment block.
// Vercel sends Authorization: Bearer <CRON_SECRET> automatically.
// The pipeline runs fire-and-forget; this route returns immediately.
import { NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

// Vercel Pro/Enterprise allows up to 300 s for cron functions.
// We return before the timeout since the pipeline runs in the background.
export const maxDuration = 60

export async function GET(request: Request): Promise<NextResponse> {
  // Vercel injects Authorization: Bearer <CRON_SECRET> on cron calls.
  // For manual/test calls, the same secret is required.
  const cronSecret = process.env.CRON_SECRET
  const authHeader = request.headers.get('authorization')

  if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  // Fire-and-forget: the Node.js runtime keeps the pipeline running
  // after the HTTP response is sent (same pattern as /api/pipeline/trigger).
  setImmediate(() => {
    import('@/lib/pipeline/runner')
      .then(({ runPipeline }) => runPipeline())
      .catch(err => console.error('[cron/pipeline] Run failed:', err))
  })

  return NextResponse.json({
    triggered: true,
    schedule: '0 */6 * * *',
    message: 'Pipeline started in background',
  })
}
