import { getMeetings } from '@/lib/data'
import { BOARD_CONFIGS } from '@/lib/types'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'
import { notFound } from 'next/navigation'
import type { MeetingCard } from '@/lib/types'

export const revalidate = 60

const DOT_COLORS: Record<string, string> = {
  'board-of-supervisors': '#0d9488',
  'planning-commission':  '#d97706',
  'lcps-school-board':    '#2563eb',
  'advisory-boards':      '#7c3aed',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

function UrgencyBadge({ urgency }: { urgency: string }) {
  const cls = urgency === 'significant' ? 'badge-urgent'
    : urgency === 'notable' ? 'badge-notable'
    : 'badge-routine'
  return <span className={cls}>{urgency}</span>
}

export default async function BoardPage({
  params,
  searchParams,
}: {
  params: { slug: string }
  searchParams: { page?: string }
}) {
  const board = BOARD_CONFIGS.find(b => b.slug === params.slug)
  if (!board) notFound()

  const page = Math.max(1, parseInt(searchParams.page ?? '1', 10))
  const limit = 12

  const data = await getMeetings(params.slug, page, limit).catch(() => null)
  const meetings: MeetingCard[] = (data as any)?.meetings ?? []
  const pagination = (data as any)?.pagination

  const dotColor = DOT_COLORS[params.slug] ?? '#71717a'

  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          {/* Hero header */}
          <div className="board-hero" data-reveal>
            <div className="board-hero-inner">
              <div className="board-hero-eyebrow">
                <span className="board-dot" style={{ background: dotColor }} />
                Board
              </div>
              <h1 className="board-hero-title">{board.title}</h1>
              <p className="board-hero-meta">{board.meta}</p>
            </div>
          </div>

          {/* Meeting cards */}
          <div className="meeting-list stagger-children">
            {meetings.length === 0 && (
              <div style={{ padding: '32px 0', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: 13 }}>
                No meetings found yet — check back after the pipeline runs.
              </div>
            )}
            {meetings.map(m => (
              <a key={m.id} href={`/meetings/${m.id}`} className="meeting-card-link">
                <div className="meeting-card-top">
                  <span className="meeting-card-date">{formatDate(String(m.meeting_date))}</span>
                  {m.fiscal_items > 0 && <span className="badge-fiscal">$ fiscal</span>}
                  <span className={`meeting-status-badge${m.processing_status === 'completed' ? ' done' : ''}`}>
                    {m.processing_status}
                  </span>
                </div>
                <div className="meeting-card-title">{m.title}</div>
                {m.meeting_overview && (
                  <div className="meeting-card-overview">{m.meeting_overview}</div>
                )}
                <div className="meeting-card-stats">
                  <span className="meeting-card-stat"><strong>{m.total_items}</strong> agenda items</span>
                  {m.fiscal_items > 0 && (
                    <span className="meeting-card-stat"><strong>{m.fiscal_items}</strong> fiscal</span>
                  )}
                  {m.fiscal_total && (
                    <span className="meeting-card-stat"><strong>{m.fiscal_total}</strong> spending</span>
                  )}
                </div>
              </a>
            ))}
          </div>

          {/* Pagination */}
          {pagination && (pagination.page > 1 || pagination.has_next) && (
            <div className="pagination">
              <a
                href={`/boards/${params.slug}?page=${page - 1}`}
                className={`pagination-btn${page <= 1 ? ' disabled' : ''}`}
              >
                ← Previous
              </a>
              <span className="pagination-info">Page {page}</span>
              <a
                href={`/boards/${params.slug}?page=${page + 1}`}
                className={`pagination-btn${!pagination.has_next ? ' disabled' : ''}`}
              >
                Next →
              </a>
            </div>
          )}

          <div style={{ height: 32 }} />
        </div>
      </div>

      <Footer />
    </div>
  )
}
