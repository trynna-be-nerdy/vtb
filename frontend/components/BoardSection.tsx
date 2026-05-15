import type { MeetingCard } from '@/lib/types'

type DotColor = 'teal' | 'amber' | 'blue' | 'purple'

const DOT_TO_STICKY: Record<DotColor, string> = {
  blue:   'sticky-blue',
  teal:   'sticky-teal',
  amber:  'sticky-amber',
  purple: 'sticky-purple',
}

interface BoardSectionProps {
  dot: DotColor
  title: string
  meta: string
  meetings: MeetingCard[]
  isAdvisory?: boolean
  slug: string
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function urgencyBadge(meeting: MeetingCard): { cls: string; label: string } {
  if (meeting.fiscal_items > 3 || meeting.total_items > 12)
    return { cls: 'b-sig', label: 'Significant' }
  if (meeting.fiscal_items > 0 || meeting.total_items > 6)
    return { cls: 'b-notable', label: 'Notable' }
  return { cls: 'b-routine', label: 'Routine' }
}

function StickyNote({
  meeting,
  colorClass,
}: {
  meeting: MeetingCard
  colorClass: string
}) {
  const badge = urgencyBadge(meeting)
  const title = meeting.top_decisions?.[0] ?? meeting.title
  const summary = meeting.meeting_overview ?? 'No summary available for this meeting.'
  const hasSchool = meeting.title.includes('School')

  return (
    <div className={`sticky ${colorClass}`}>
      <div className="sticky-top">
        <span className="sticky-date">{formatDate(meeting.meeting_date)}</span>
        <span className={`badge ${badge.cls}`}>{badge.label}</span>
      </div>
      <div className="sticky-title">{title}</div>
      <div className="sticky-summary">{summary}</div>
      {(hasSchool || meeting.fiscal_items > 0) && (
        <div className="sticky-tags">
          {hasSchool && <span className="tag">Education</span>}
          {meeting.fiscal_items > 0 && <span className="tag-fiscal">$ Fiscal</span>}
        </div>
      )}
    </div>
  )
}

function EmptySticky({ colorClass }: { colorClass: string }) {
  return (
    <div className={`sticky ${colorClass}`} style={{ opacity: 0.45 }}>
      <div className="sticky-title" style={{ color: 'rgba(0,0,0,0.35)', fontSize: 12 }}>
        No recent meetings
      </div>
    </div>
  )
}

function AdvisorySticky({ meeting }: { meeting: MeetingCard }) {
  const itemCount = meeting.total_items
  const badgeCls = itemCount > 3 ? 'b-notable' : 'b-teal'

  return (
    <div className="comm-card">
      <div className="sticky-top">
        <span className="comm-name">{meeting.title}</span>
        <span className={`badge ${badgeCls}`}>{itemCount} items</span>
      </div>
      <div className="comm-date">
        {formatDate(meeting.meeting_date)} · Advisory
      </div>
      <div className="comm-preview">
        {meeting.meeting_overview ?? meeting.top_decisions?.[0] ?? 'No summary available.'}
      </div>
    </div>
  )
}

export function BoardSection({
  dot,
  title,
  meta,
  meetings,
  isAdvisory = false,
  slug,
}: BoardSectionProps) {
  const cardCount = isAdvisory ? 4 : 3
  const colorClass = DOT_TO_STICKY[dot]
  const totalItems = meetings.reduce((s, m) => s + m.total_items, 0)
  const meetingCount = meetings.length

  return (
    <div className="section">
      {/* Section header */}
      <div className="section-header">
        <div>
          <div className="section-left">
            <div className={`dot dot-${dot}`} />
            <div className="section-title">{title}</div>
          </div>
          <div className="section-meta">{meta}</div>
        </div>
        <a href={`/boards/${slug}`} className="view-all">
          View all →
        </a>
      </div>

      {/* Sticky note wall */}
      <div className={isAdvisory ? 'comm-grid' : 'wall'}>
        {meetings.slice(0, cardCount).map(m =>
          isAdvisory ? (
            <AdvisorySticky key={m.id} meeting={m} />
          ) : (
            <StickyNote key={m.id} meeting={m} colorClass={colorClass} />
          )
        )}
        {meetings.length < cardCount &&
          !isAdvisory &&
          Array.from({ length: cardCount - meetings.length }).map((_, i) => (
            <EmptySticky key={`empty-${i}`} colorClass={colorClass} />
          ))}
      </div>

      {/* Section footer */}
      <div className="section-footer">
        <div className="footer-stat">
          {meetingCount > 0
            ? `${meetingCount} meeting${meetingCount !== 1 ? 's' : ''} · ${totalItems} agenda items · Source: county portal`
            : 'No meetings found · Source: county meeting portal'}
        </div>
        <a href={`/boards/${slug}`} className="footer-link">
          All {title} meetings →
        </a>
      </div>
    </div>
  )
}
