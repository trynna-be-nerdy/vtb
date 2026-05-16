import { getCategoryFeed, CATEGORY_LABELS } from '@/lib/data'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'
import { notFound } from 'next/navigation'
import type { AgendaItemCard } from '@/lib/types'

export const revalidate = 60

const BOARD_LABELS: Record<string, string> = {
  'board-of-supervisors': 'Supervisors',
  'planning-commission':  'Planning',
  'lcps-school-board':    'LCPS',
  'advisory-boards':      'Advisory',
}

function formatDate(dateStr: string): string {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
  })
}

function UrgencyBadge({ urgency }: { urgency: string }) {
  const cls = urgency === 'significant' ? 'badge-urgent'
    : urgency === 'notable' ? 'badge-notable'
    : 'badge-routine'
  return <span className={cls}>{urgency}</span>
}

export default async function CategoryPage({
  params,
  searchParams,
}: {
  params: { slug: string }
  searchParams: { page?: string }
}) {
  const label = CATEGORY_LABELS[params.slug]
  if (!label) notFound()

  const page = Math.max(1, parseInt(searchParams.page ?? '1', 10))
  const limit = 15

  const data = await getCategoryFeed(params.slug, page, limit).catch(() => null)
  const items: AgendaItemCard[] = (data as any)?.items ?? []
  const pagination = (data as any)?.pagination

  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          {/* Hero */}
          <div className="category-hero" data-reveal>
            <div className="category-hero-inner">
              <div className="category-hero-label">Category</div>
              <h1 className="category-hero-title">{label}</h1>
              {pagination?.total != null && (
                <div style={{ fontSize: 12, color: 'var(--color-text-secondary)', marginTop: 4 }}>
                  {pagination.total} agenda items
                </div>
              )}
            </div>
          </div>

          {/* Agenda item cards */}
          <div className="agenda-item-list stagger-children">
            {items.length === 0 && (
              <div style={{ padding: '32px 0', textAlign: 'center', color: 'var(--color-text-secondary)', fontSize: 13 }}>
                No items in this category yet.
              </div>
            )}
            {items.map(item => (
              <div key={item.id} className="agenda-item-card" data-reveal>
                <div className="agenda-item-top">
                  <UrgencyBadge urgency={item.urgency} />
                  {item.fiscal_impact && <span className="badge-fiscal">$ fiscal</span>}
                  {item.secondary_tags?.slice(0, 2).map(t => (
                    <span key={t} className="chip chip-gray">{t}</span>
                  ))}
                </div>
                <div className="agenda-item-title">{item.title}</div>
                <div className="agenda-item-summary">{item.summary}</div>
                <div className="agenda-item-footer">
                  <span className="agenda-item-meeting">
                    <a href={`/meetings/${item.meeting_id}`}>View meeting →</a>
                  </span>
                  {item.source_pdf_url && (
                    <a
                      href={item.source_pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="chip chip-gray"
                      style={{ fontSize: 10, textDecoration: 'none' }}
                    >
                      Source PDF
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {pagination && (pagination.page > 1 || pagination.has_next) && (
            <div className="pagination">
              <a
                href={`/categories/${params.slug}?page=${page - 1}`}
                className={`pagination-btn${page <= 1 ? ' disabled' : ''}`}
              >
                ← Previous
              </a>
              <span className="pagination-info">Page {page}</span>
              <a
                href={`/categories/${params.slug}?page=${page + 1}`}
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
