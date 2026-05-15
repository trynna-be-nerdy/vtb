import type { MeetingCard } from '@/lib/types'

type DotColor = 'teal' | 'amber' | 'blue' | 'purple'

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
  return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

function urgencyBadge(meeting: MeetingCard): { cls: string; label: string } {
  if (meeting.fiscal_items > 3 || meeting.total_items > 12)
    return { cls: 'b-sig', label: 'Significant' }
  if (meeting.fiscal_items > 0 || meeting.total_items > 6)
    return { cls: 'b-notable', label: 'Notable' }
  return { cls: 'b-routine', label: 'Routine' }
}

function MeetingCard({ meeting }: { meeting: MeetingCard }) {
  const badge = urgencyBadge(meeting)
  const title = meeting.top_decisions?.[0] ?? meeting.title
  const summary = meeting.meeting_overview ?? 'No summary available for this meeting.'
  const tags = [meeting.title.includes('School') ? 'Schools & Education' : null].filter(Boolean)

  return (
    <div className="card">
      <div className="card-top">
        <div className="card-date">{formatDate(meeting.meeting_date)}</div>
        <div className={`badge ${badge.cls}`}>{badge.label}</div>
      </div>
      <div className="card-title">{title}</div>
      <div className="card-summary">{summary}</div>
      {(tags.length > 0 || meeting.fiscal_items > 0) && (
        <div className="card-tags">
          {tags.map(t => (
            <div key={t} className="tag">{t}</div>
          ))}
          {meeting.fiscal_items > 0 && (
            <div className="tag-fiscal">$ Fiscal</div>
          )}
        </div>
      )}
    </div>
  )
}

function AdvisoryCard({ meeting }: { meeting: MeetingCard }) {
  const itemCount = meeting.total_items
  const badgeCls = itemCount > 3 ? 'b-notable' : 'b-teal'

  return (
    <div className="comm-card">
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div className="comm-name">{meeting.title}</div>
        <div className={`badge ${badgeCls}`}>{itemCount} items</div>
      </div>
      <div className="comm-date">
        Last met {formatDate(meeting.meeting_date)} · Advisory Board
      </div>
      <div className="comm-preview">
        {meeting.meeting_overview ?? meeting.top_decisions?.[0] ?? 'No summary available.'}
      </div>
    </div>
  )
}

function EmptyCards({ count, isAdvisory }: { count: number; isAdvisory: boolean }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        isAdvisory ? (
          <div key={i} className="comm-card">
            <div className="empty-state" style={{ padding: '20px 0' }}>No recent activity</div>
          </div>
        ) : (
          <div key={i} className="card">
            <div className="empty-state">No recent meetings</div>
          </div>
        )
      ))}
    </>
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
  const totalItems = meetings.reduce((s, m) => s + m.total_items, 0)
  const meetingCount = meetings.length

  return (
    <div className="section">
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

      <div className={isAdvisory ? 'comm-grid' : 'cards'}>
        {meetings.slice(0, cardCount).map(m =>
          isAdvisory ? (
            <AdvisoryCard key={m.id} meeting={m} />
          ) : (
            <MeetingCard key={m.id} meeting={m} />
          ),
        )}
        {meetings.length < cardCount && (
          <EmptyCards
            count={cardCount - meetings.length}
            isAdvisory={isAdvisory}
          />
        )}
      </div>

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
