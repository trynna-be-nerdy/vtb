/**
 * Server-Sent Events endpoint — replaces the Python WebSocket /ws/updates.
 * Subscribes to Redis pub/sub and streams events to the client.
 *
 * Usage (client-side):
 *   const es = new EventSource('/api/updates')
 *   es.onmessage = (e) => console.log(JSON.parse(e.data))
 */

import { NextResponse } from 'next/server'
import Redis from 'ioredis'
import { PUBSUB_CHANNEL } from '@/lib/redis'

export const runtime = 'nodejs'
// Disable response caching for SSE
export const dynamic = 'force-dynamic'

export async function GET() {
  const encoder = new TextEncoder()

  const stream = new ReadableStream({
    start(controller) {
      // Each SSE connection needs its own Redis subscriber
      const subscriber = new Redis(
        process.env.REDIS_URL ?? 'redis://localhost:6379/0',
        { enableReadyCheck: false, lazyConnect: true },
      )

      subscriber.subscribe(PUBSUB_CHANNEL, (err) => {
        if (err) {
          controller.error(err)
          return
        }
      })

      subscriber.on('message', (_channel, message) => {
        controller.enqueue(encoder.encode(`data: ${message}\n\n`))
      })

      // Send a heartbeat every 30 s to keep the connection alive
      const heartbeat = setInterval(() => {
        try {
          controller.enqueue(encoder.encode(': heartbeat\n\n'))
        } catch {
          clearInterval(heartbeat)
        }
      }, 30_000)

      // Cleanup when the client disconnects
      return () => {
        clearInterval(heartbeat)
        subscriber.unsubscribe(PUBSUB_CHANNEL)
        subscriber.quit()
      }
    },
  })

  return new NextResponse(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache, no-transform',
      Connection: 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  })
}
