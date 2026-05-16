import { getMeeting } from '@/lib/data'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'
import { AgendaItemAccordion } from '@/components/AgendaItemAccordion'
import { notFound } from 'next/navigation'
import type { MeetingDetail } from '@/lib/types'

export const dynamic = 'force-dynamic'

const BOARD_LABELS: Record<string, string> = {
  'board-of-supervisors': 'Board of Supervisors',
  'planning-commission':  'Planning Commission',
  'lcps-school-board':    'LCPS School Board',
  'advisory-boards':      'Advisory Boards',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
}

export default async function MeetingDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const id = parseInt(params.id, 10)
  if (isNaN(id)) notFound()

  const data = await getMeeting(id).catch(() => null)
  if (!data) notFound()

  const meeting = (data as { meeting: MeetingDetail }).meeting

  return (
    <div className="site">
      <Navbar />

      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          {/* ── Back link ── */}
          <div className="meeting-detail-back">
            <a href={`/boards/${meeting.board_slug}`} className="back-link">
              ← {BOARD_LABELS[meeting.board_slug] ?? 'Board'}
            </a>
          </div>

          {/* ── Meeting header ── */}
          <div className="meeting-detail-header">
            <div className="meeting-detail-meta">
              <span className="meeting-detail-board">
                {BOARD_LABELS[meeting.board_slug] ?? meeting.board_slug}
              </span>
              <span className="meeting-detail-sep">·</span>
              <span className="meeting-detail-date">{formatDate(meeting.meeting_date)}</span>
            </div>
            <h1 className="meeting-detail-title">{meeting.title}</h1>

            {/* Quick stats bar */}
            <div className="meeting-stats">
              <div className="meeting-stat">
                <div className="meeting-stat-value">{meeting.total_items}</div>
                <div className="meeting-stat-label">Agenda items</div>
              </div>
              <div className="meeting-stat">
                <div className="meeting-stat-value">{meeting.fiscal_items}</div>
                <div className="meeting-stat-label">Fiscal items</div>
              </div>
              {meeting.fiscal_total && (
                <div className="meeting-stat">
                  <div className="meeting-stat-value">{meeting.fiscal_total}</div>
                  <div className="meeting-stat-label">Total spending</div>
                </div>
              )}
              {meeting.source_url && (
                <a
                  href={meeting.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="meeting-stat meeting-stat-link"
                >
                  <div className="meeting-stat-value" style={{ fontSize: 18 }}>↗</div>
                  <div className="meeting-stat-label">Official source</div>
                </a>
              )}
            </div>
          </div>

          {/* ── Meeting overview ── */}
          {meeting.meeting_overview && (
            <div className="meeting-section">
              <div className="meeting-section-label">Meeting Overview</div>
              <p className="meeting-overview-text">{meeting.meeting_overview}</p>
            </div>
          )}

          {/* ── Top decisions ── */}
          {meeting.top_decisions && meeting.top_decisions.length > 0 && (
            <div className="meeting-section">
              <div className="meeting-section-label">Top Decisions</div>
              <div className="top-decisions-grid">
                {meeting.top_decisions.slice(0, 3).map((d, i) => (
                  <div key={i} className="top-decision-card">
                    <div className="top-decision-num">{i + 1}</div>
                    <div className="top-decision-text">{d}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── Agenda items accordion ── */}
          <div className="meeting-section">
            <div className="meeting-section-label">
              Agenda Items
              {meeting.agenda_items.length > 0 && (
                <span className="meeting-section-count">{meeting.agenda_items.length}</span>
              )}
            </div>
            <AgendaItemAccordion items={meeting.agenda_items} />
          </div>

          {/* ── Supporting documents ── */}
          {meeting.supporting_documents.length > 0 && (
            <div className="meeting-section">
              <div className="meeting-section-label">Supporting Documents</div>
              <div className="docs-list">
                {meeting.supporting_documents.map(doc => (
                  <a
                    key={doc.id}
                    href={doc.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="doc-item"
                  >
                    <span className="doc-icon">📄</span>
                    <span className="doc-title">{doc.title ?? 'Document'}</span>
                    {doc.doc_type && (
                      <span className="chip chip-gray" style={{ fontSize: 9.5 }}>{doc.doc_type}</span>
                    )}
                    <span className="doc-arrow">→</span>
                  </a>
                ))}
              </div>
            </div>
          )}

          {/* ── Next meeting notes ── */}
          {meeting.next_meeting_notes && (
            <div className="meeting-section">
              <div className="meeting-section-label">Next Meeting</div>
              <p className="meeting-overview-text">{meeting.next_meeting_notes}</p>
            </div>
          )}

          <div style={{ height: 48 }} />
        </div>
      </div>

      <Footer />
    </div>
  )
}
