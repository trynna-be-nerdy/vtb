import { getMeetingsByMonth, type MeetingCalendarItem } from '@/lib/data'
import { BOARD_CONFIGS } from '@/lib/types'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'
import Link from 'next/link'
import type { Metadata } from 'next'

export const revalidate = 60
export const dynamic = 'force-dynamic'

export const metadata: Metadata = {
  title: 'Meeting Calendar — View the Board',
  description: 'Browse all Loudoun County government meetings by date. Filter by board.',
}

const BOARD_COLORS: Record<string, { color: string; abbr: string; label: string }> = {
  'board-of-supervisors': { color: '#0d9488', abbr: 'BOS',      label: 'Board of Supervisors' },
  'planning-commission':  { color: '#d97706', abbr: 'Planning',  label: 'Planning Commission' },
  'lcps-school-board':    { color: '#2563eb', abbr: 'LCPS',      label: 'LCPS School Board' },
  'advisory-boards':      { color: '#7c3aed', abbr: 'Advisory',  label: 'Advisory Boards' },
}

const MONTH_NAMES = [
  'January','February','March','April','May','June',
  'July','August','September','October','November','December',
]

const DAY_NAMES = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']

function prevMonth(year: number, month: number) {
  return month === 1 ? { y: year - 1, m: 12 } : { y: year, m: month - 1 }
}
function nextMonth(year: number, month: number) {
  return month === 12 ? { y: year + 1, m: 1 } : { y: year, m: month + 1 }
}
function monthParam(y: number, m: number) {
  return `${y}-${String(m).padStart(2, '0')}`
}

function groupByDate(meetings: MeetingCalendarItem[]): Map<string, MeetingCalendarItem[]> {
  const map = new Map<string, MeetingCalendarItem[]>()
  for (const m of meetings) {
    const key = m.meeting_date.slice(0, 10)
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(m)
  }
  return map
}

export default async function CalendarPage({
  searchParams,
}: {
  searchParams: { month?: string; board?: string }
}) {
  const now = new Date()
  const todayStr = now.toISOString().slice(0, 10)

  let year = now.getFullYear()
  let month = now.getMonth() + 1
  if (searchParams.month && /^\d{4}-\d{2}$/.test(searchParams.month)) {
    const [y, m] = searchParams.month.split('-').map(Number)
    if (y >= 2020 && y <= 2030 && m >= 1 && m <= 12) { year = y; month = m }
  }

  const activeBoard = BOARD_CONFIGS.find(b => b.slug === searchParams.board)?.slug ?? null

  const data = await getMeetingsByMonth(year, month, activeBoard).catch(() => ({ meetings: [] as MeetingCalendarItem[] }))

  const meetings = data.meetings
  const byDate = groupByDate(meetings)

  const firstDayOfMonth = new Date(year, month - 1, 1)
  const daysInMonth = new Date(year, month, 0).getDate()
  const startDow = firstDayOfMonth.getDay()

  const cells: (number | null)[] = [
    ...Array(startDow).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ]
  while (cells.length % 7 !== 0) cells.push(null)

  const prev = prevMonth(year, month)
  const next = nextMonth(year, month)
  const boardSuffix = activeBoard ? `&board=${activeBoard}` : ''
  const prevHref = `/calendar?month=${monthParam(prev.y, prev.m)}${boardSuffix}`
  const nextHref = `/calendar?month=${monthParam(next.y, next.m)}${boardSuffix}`
  const pad = (n: number) => String(n).padStart(2, '0')

  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">

          {/* ── Calendar header ── */}
          <div className="calendar-page-header" data-reveal>
            <div className="calendar-title-row">
              <Link href={prevHref} className="calendar-nav-btn" aria-label="Previous month">←</Link>
              <h1 className="calendar-month-title">{MONTH_NAMES[month - 1]} {year}</h1>
              <Link href={nextHref} className="calendar-nav-btn" aria-label="Next month">→</Link>
            </div>

            <div className="calendar-filter-tabs">
              <Link
                href={`/calendar?month=${monthParam(year, month)}`}
                className={`calendar-filter-tab ${!activeBoard ? 'calendar-filter-tab-active' : ''}`}
              >
                All Boards
              </Link>
              {BOARD_CONFIGS.map(b => {
                const cfg = BOARD_COLORS[b.slug]
                return (
                  <Link
                    key={b.slug}
                    href={`/calendar?month=${monthParam(year, month)}&board=${b.slug}`}
                    className={`calendar-filter-tab ${activeBoard === b.slug ? 'calendar-filter-tab-active' : ''}`}
                    style={activeBoard === b.slug ? { borderBottomColor: cfg.color, color: cfg.color } : {}}
                  >
                    {cfg.abbr}
                  </Link>
                )
              })}
            </div>
          </div>

          {/* ── Calendar grid ── */}
          <div className="calendar-grid-wrapper" data-reveal>
            <div className="calendar-grid">
              {DAY_NAMES.map(d => (
                <div key={d} className="calendar-day-header">{d}</div>
              ))}

              {cells.map((day, i) => {
                if (day === null) {
                  return <div key={`pad-${i}`} className="calendar-cell calendar-cell-empty" />
                }
                const dateKey = `${year}-${pad(month)}-${pad(day)}`
                const dayMeetings = byDate.get(dateKey) ?? []
                const isToday = dateKey === todayStr
                const isPast = dateKey < todayStr

                return (
                  <div
                    key={dateKey}
                    className={`calendar-cell${isToday ? ' calendar-cell-today' : ''}${isPast && !isToday ? ' calendar-cell-past' : ''}`}
                  >
                    <span className="calendar-day-num">{day}</span>
                    <div className="calendar-meetings">
                      {dayMeetings.slice(0, 3).map(m => {
                        const cfg = BOARD_COLORS[m.board_slug]
                        return (
                          <Link
                            key={m.id}
                            href={m.processing_status === 'completed' ? `/meetings/${m.id}` : '#'}
                            className="calendar-meeting-badge"
                            style={{ borderLeftColor: cfg?.color ?? '#71717a' }}
                            title={m.title}
                          >
                            <span className="calendar-badge-abbr" style={{ color: cfg?.color ?? '#71717a' }}>
                              {cfg?.abbr ?? m.board_slug}
                            </span>
                            <span className="calendar-badge-title">{m.title}</span>
                            {m.processing_status !== 'completed' && (
                              <span className="calendar-badge-pending">pending</span>
                            )}
                          </Link>
                        )
                      })}
                      {dayMeetings.length > 3 && (
                        <span className="calendar-more">+{dayMeetings.length - 3} more</span>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* ── Empty state ── */}
          {meetings.length === 0 && (
            <div className="calendar-empty" data-reveal>
              <p className="calendar-empty-title">No meetings found for {MONTH_NAMES[month - 1]} {year}</p>
              <p className="calendar-empty-sub">
                The pipeline runs every 6 hours to discover new documents from Loudoun County and LCPS.
                {' '}Try a different month or check back later.
              </p>
              <Link href="/calendar" className="calendar-empty-link">← Back to this month</Link>
            </div>
          )}

          {/* ── Board legend ── */}
          <div className="calendar-legend" data-reveal>
            {Object.entries(BOARD_COLORS).map(([slug, cfg]) => (
              <span key={slug} className="calendar-legend-item">
                <span className="calendar-legend-dot" style={{ background: cfg.color }} />
                {cfg.label}
              </span>
            ))}
          </div>

        </div>
      </div>

      <Footer />
    </div>
  )
}
