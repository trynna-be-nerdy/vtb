import postgres from 'postgres'

declare global {
  // eslint-disable-next-line no-var
  var __sql: ReturnType<typeof postgres> | undefined
}

export const sql =
  globalThis.__sql ??
  postgres(
    process.env.DATABASE_URL ?? 'postgresql://vtb:vtbpassword@localhost:5432/vtb',
    {
      max: 10,
      idle_timeout: 20,
      connect_timeout: 10,
    },
  )

if (process.env.NODE_ENV !== 'production') {
  globalThis.__sql = sql
}

// ── Date serialisation helpers ────────────────────────────────────────────────

const DATE_COLS = new Set(['meeting_date', 'created_at', 'updated_at', 'started_at', 'finished_at'])

export function serializeRow<T extends Record<string, unknown>>(row: T): T {
  return Object.fromEntries(
    Object.entries(row).map(([k, v]) => {
      if (v instanceof Date) {
        // date-only columns return midnight UTC — format as YYYY-MM-DD
        if (DATE_COLS.has(k) && v.toISOString().endsWith('T00:00:00.000Z')) {
          return [k, v.toISOString().split('T')[0]]
        }
        return [k, v.toISOString()]
      }
      return [k, v]
    }),
  ) as T
}

export function serializeRows<T extends Record<string, unknown>>(rows: T[]): T[] {
  return rows.map(serializeRow)
}
