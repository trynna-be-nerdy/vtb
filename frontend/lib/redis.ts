import Redis from 'ioredis'

declare global {
  // eslint-disable-next-line no-var
  var __redis: Redis | undefined
}

const redisInstance =
  globalThis.__redis ??
  new Redis(process.env.REDIS_URL ?? 'redis://localhost:6379/0', {
    maxRetriesPerRequest: 1,
    enableReadyCheck: false,
    lazyConnect: true,
    connectTimeout: 2000,
    commandTimeout: 2000,
  })

// Prevent "unhandled error event" crashes when Redis is unavailable
redisInstance.on('error', () => {})

export const redis = redisInstance

if (process.env.NODE_ENV !== 'production') {
  globalThis.__redis = redis
}

export const PUBSUB_CHANNEL = 'vtb:updates'

const CACHE_TTL = parseInt(process.env.CACHE_TTL_SECONDS ?? '900', 10)
const SEARCH_TTL = parseInt(process.env.SEARCH_CACHE_TTL_SECONDS ?? '300', 10)
export const HEALTH_TTL = parseInt(process.env.HEALTH_CACHE_TTL_SECONDS ?? '30', 10)
export { CACHE_TTL, SEARCH_TTL }

// ── Cache helpers ─────────────────────────────────────────────────────────────

export async function cacheGet(key: string): Promise<unknown> {
  try {
    const val = await redis.get(key)
    return val ? (JSON.parse(val) as unknown) : null
  } catch {
    return null
  }
}

export async function cacheSet(
  key: string,
  value: unknown,
  ttl: number = CACHE_TTL,
): Promise<void> {
  try {
    await redis.set(key, JSON.stringify(value), 'EX', ttl)
  } catch {
    // Cache failures are non-fatal
  }
}

export async function cacheDeletePattern(pattern: string): Promise<void> {
  try {
    const keys = await redis.keys(pattern)
    if (keys.length > 0) await redis.del(...keys)
  } catch {
    // non-fatal
  }
}

export async function publishUpdate(payload: Record<string, unknown>): Promise<void> {
  try {
    await redis.publish(PUBSUB_CHANNEL, JSON.stringify(payload))
  } catch {
    // non-fatal
  }
}
