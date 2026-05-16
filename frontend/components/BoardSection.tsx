import type { MeetingCard } from '@/lib/types'
import { DecisionsAccordion, type DecisionGroup } from './Accordion'

type DotColor = 'teal' | 'amber' | 'blue' | 'purple'

const DOT_TO_STICKY: Record<DotColor, string> = {
  blue:   'sticky-blue',
  teal:   'sticky-teal',
  amber:  'sticky-amber',
  purple: 'sticky-purple',
}

// Maps board dot color → HeroUI chip class
const DOT_TO_CHIP: Record<DotColor, string> = {
  blue:   'chip-blue',
  teal:   'chip-teal',
  amber:  'chip-amber',
  purple: 'chip-purple',
}

// Maps board dot color → accent hex for accordion dots
const DOT_TO_HEX: Record<DotColor, string> = {
  blue:   '#378add',
  teal:   '#1d9e75',
  amber:  '#ba7517',
  purple: '#7f77dd',
}

// DaisyUI badge variants replacing the old hand-coded b-sig/b-notable/b-routine
const URGENCY_BADGE: Record<'Significant' | 'Notable' | 'Routine', string> = {
  Significant: 'badge badge-error badge-sm',
  Notable:     'badge badge-warning badge-sm',
  Routine:     'badge badge-ghost badge-sm',
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

function urgencyBadge(meeting: MeetingCard): { cls: string; label: 'Significant' | 'Notable' | 'Routine' } {
  if (meeting.fiscal_items > 3 || meeting.total_items > 12) return { cls: URGENCY_BADGE.Significant, label: 'Significant' }
  if (meeting.fiscal_items > 0 || meeting.total_items > 6)  return { cls: URGENCY_BADGE.Notable,     label: 'Notable' }
  return { cls: URGENCY_BADGE.Routine, label: 'Routine' }
}

function StickyNote({
  meeting,
  colorClass,
  chipClass,
}: {
  meeting: MeetingCard
  colorClass: string
  chipClass: string
}) {
  const badge = urgencyBadge(meeting)
  const title = meeting.top_decisions?.[0] ?? meeting.title
  const summary = meeting.meeting_overview ?? 'No summary available for this meeting.'
  const hasSchool = meeting.title.includes('School')

  return (
    <div className={`sticky ${colorClass}`}>
      <div className="sticky-top">
        <span className="sticky-date">{formatDate(meeting.meeting_date)}</span>
        {/* DaisyUI badge replaces old .badge .b-sig/notable/routine */}
        <span className={badge.cls} style={{ fontSize: 9, padding: '1px 7px' }}>
          {badge.label}
        </span>
      </div>
      <div className="sticky-title">{title}</div>
      <div className="sticky-summary">{summary}</div>
      {/* HeroUI chip tags replace old .tag / .tag-fiscal */}
      {(hasSchool || meeting.fiscal_items > 0) && (
        <div className="sticky-tags">
          {hasSchool && <span className={`chip ${chipClass}`}>Education</span>}
          {meeting.fiscal_items > 0 && <span className="chip chip-green">$ Fiscal</span>}
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

function AdvisorySticky({ meeting, chipClass }: { meeting: MeetingCard; chipClass: string }) {
  const itemCount = meeting.total_items
  // DaisyUI badge for advisory item count
  const badgeCls = itemCount > 3
    ? 'badge badge-warning badge-sm'
    : 'badge badge-success badge-sm'

  return (
    <div className="comm-card">
      <div className="sticky-top">
        <span className="comm-name">{meeting.title}</span>
        <span className={badgeCls} style={{ fontSize: 9, padding: '1px 7px' }}>
          {itemCount} items
        </span>
      </div>
      <div className="comm-date">
        {formatDate(meeting.meeting_date)} · Advisory
      </div>
      <div className="comm-preview">
        {meeting.meeting_overview ?? meeting.top_decisions?.[0] ?? 'No summary available.'}
      </div>
      {/* HeroUI chip for advisory context */}
      <div style={{ marginTop: 4 }}>
        <span className={`chip ${chipClass}`} style={{ fontSize: 9.5 }}>Advisory</span>
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
  const chipClass  = DOT_TO_CHIP[dot]
  const accentHex  = DOT_TO_HEX[dot]
  const totalItems = meetings.reduce((s, m) => s + m.total_items, 0)
  const meetingCount = meetings.length

  // Build serializable accordion items from top_decisions
  const accordionItems: DecisionGroup[] = meetings
    .filter(m => (m.top_decisions?.length ?? 0) > 0)
    .map(m => ({
      meetingDate:  formatDate(m.meeting_date),
      meetingTitle: m.title,
      decisions:    m.top_decisions ?? [],
      totalItems:   m.total_items,
    }))

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
            <AdvisorySticky key={m.id} meeting={m} chipClass={chipClass} />
          ) : (
            <StickyNote key={m.id} meeting={m} colorClass={colorClass} chipClass={chipClass} />
          )
        )}
        {meetings.length < cardCount && !isAdvisory &&
          Array.from({ length: cardCount - meetings.length }).map((_, i) => (
            <EmptySticky key={`empty-${i}`} colorClass={colorClass} />
          ))}
      </div>

      {/* Flowbite accordion — key decisions, collapsible */}
      <DecisionsAccordion items={accordionItems} accentColor={accentHex} />

      {/* Section footer */}
      <div className="section-footer">
        <div className="footer-stat">
          {meetingCount > 0
            ? `${meetingCount} meeting${meetingCount !== 1 ? 's' : ''} · ${totalItems} agenda items · Source: county portal`
            : 'No meetings found · Source: county meeting portal'}
        </div>
        <a href={`/boards/${slug}`} className="footer-link">
          All meetings →
        </a>
      </div>
    </div>
  )
}
