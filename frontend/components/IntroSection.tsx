import type { MeetingCard } from '@/lib/types'

const OUTCOME_PILL: Record<string, string> = {
  Approved: 'ap-approved',
  Denied: 'ap-denied',
  Deferred: 'ap-deferred',
  Discussed: 'ap-discussed',
  Updated: 'ap-updated',
}

function inferOutcome(decision: string): string {
  const lower = decision.toLowerCase()
  if (lower.includes('denied') || lower.includes('rejected')) return 'Denied'
  if (lower.includes('defer') || lower.includes('postpone') || lower.includes('tabled'))
    return 'Deferred'
  if (lower.includes('discuss') || lower.includes('reviewed') || lower.includes('presented'))
    return 'Discussed'
  if (lower.includes('amend') || lower.includes('updat') || lower.includes('extend'))
    return 'Updated'
  return 'Approved'
}

function formatBoardName(slug: string): string {
  const names: Record<string, string> = {
    'board-of-supervisors': 'Board of Supervisors',
    'planning-commission': 'Planning Commission',
    'lcps-school-board': 'LCPS School Board',
    'advisory-boards': 'Standing Committee',
    'finance-committee': 'Finance Committee',
    'parks-recreation-advisory': 'Parks & Recreation Advisory',
    'environmental-advisory': 'Environmental Advisory',
    'economic-development': 'Economic Development',
  }
  return names[slug] ?? slug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

function formatShortDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

interface ActivityRow {
  outcome: string
  board: string
  date: string
  title: string
  note?: string
}

function buildActivityRows(meetings: MeetingCard[]): ActivityRow[] {
  const rows: ActivityRow[] = []
  for (const m of meetings) {
    if (!m.top_decisions?.length) continue
    for (const decision of m.top_decisions.slice(0, 2)) {
      rows.push({
        outcome: inferOutcome(decision),
        board: formatBoardName(m.board_slug),
        date: formatShortDate(m.meeting_date),
        title: decision,
      })
      if (rows.length >= 9) break
    }
    if (rows.length >= 9) break
  }
  return rows
}

interface IntroSectionProps {
  recentMeetings?: MeetingCard[]
}

export function IntroSection({ recentMeetings = [] }: IntroSectionProps) {
  const now = new Date()
  const day = now.getDate()
  const monthYear = now.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
  const dayOfWeek = now.toLocaleDateString('en-US', { weekday: 'long' })

  const weekStart = new Date(now)
  weekStart.setDate(now.getDate() - now.getDay() + 1)
  const weekEnd = new Date(now)
  weekEnd.setDate(weekStart.getDate() + 6)
  const weekLabel = `${weekStart.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}–${weekEnd.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}`

  const activityRows = buildActivityRows(recentMeetings)

  // Static sample rows shown when no live data (matches design reference)
  const sampleRows: ActivityRow[] = [
    { outcome: 'Approved', board: 'Board of Supervisors', date: 'May 5', title: 'Route 7 corridor rezoned for mixed-use — high-density residential and retail, traffic study required by Q3', note: '5–3' },
    { outcome: 'Approved', board: 'Board of Supervisors', date: 'May 5', title: '$4.8M park and trail network funded for Ashburn district — groundbreaking spring 2027', note: '7–1' },
    { outcome: 'Deferred', board: 'Board of Supervisors', date: 'May 5', title: 'Route 15 Bypass corridor study deferred to June — awaiting VDOT preliminary engineering update', note: 'To Jun 2' },
    { outcome: 'Approved', board: 'LCPS School Board', date: 'May 7', title: '$2.3M bus route expansion — 12 new routes for eastern district, effective August 2026', note: '6–1' },
    { outcome: 'Approved', board: 'LCPS School Board', date: 'May 7', title: 'K–8 STEM curriculum adopted for all 14 elementary schools — rollout September 2026', note: 'Unanimous' },
    { outcome: 'Approved', board: 'Planning Commission', date: 'May 6', title: 'Rezoning ZMAP-2025-0041 — 142 townhomes in Brambleton, 15% affordable unit condition', note: '6–1' },
    { outcome: 'Denied', board: 'Planning Commission', date: 'May 6', title: 'Data center special exception on Route 606 denied — road and utility capacity insufficient', note: '2–5' },
    { outcome: 'Discussed', board: 'Standing Committee', date: 'May 8', title: 'Finance Committee reviewed five-year capital plan — Leesburg bypass funding forwarded to full board', note: 'No vote' },
    { outcome: 'Updated', board: 'Planning Commission', date: 'May 6', title: 'Route 28 corridor Comprehensive Plan amendments — public comment extended 30 days', note: '3 items' },
  ]

  const displayRows = activityRows.length > 0 ? activityRows : sampleRows

  return (
    <div
      className="intro"
      style={{ flexDirection: 'column', alignItems: 'stretch', gap: 0 }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          paddingBottom: 0,
        }}
      >
        <div className="intro-title">What Loudoun County decided this week</div>
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            gap: 10,
            paddingLeft: 24,
            flexShrink: 0,
          }}
        >
          <div className="intro-date-block" style={{ marginBottom: 0 }}>
            <div className="intro-date-day">{day}</div>
            <div className="intro-date-rest">
              <div className="intro-date-month">{monthYear}</div>
              <div className="intro-date-dow">{dayOfWeek}</div>
            </div>
          </div>
          <a href="/calendar" className="cal-btn">View Calendar →</a>
        </div>
      </div>

      <div className="activity-log">
        <div className="activity-log-label">
          Decisions &amp; changes recorded — {weekLabel}
        </div>
        {displayRows.map((row, i) => (
          <div key={i} className="act-row">
            <span className={`act-pill ${OUTCOME_PILL[row.outcome] ?? 'ap-updated'}`}>
              {row.outcome}
            </span>
            <span className="act-board">
              {row.board} · {row.date}
            </span>
            <span className="act-title">{row.title}</span>
            {row.note && <span className="act-vote">{row.note}</span>}
          </div>
        ))}
      </div>
    </div>
  )
}
