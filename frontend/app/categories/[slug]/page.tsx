import { getCategoryFeed, CATEGORY_LABELS } from '@/lib/data'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'
import { notFound } from 'next/navigation'
import Link from 'next/link'
import type { AgendaItemCard } from '@/lib/types'

export const revalidate = 60

const BOARD_LABELS: Record<string, string> = {
  'board-of-supervisors': 'Supervisors',
  'planning-commission':  'Planning',
  'lcps-school-board':    'LCPS',
  'advisory-boards':      'Advisory',
}

const CATEGORY_COLORS: Record<string, string> = {
  'schools-education':  '#2563eb',
  'school-construction':'#0891b2',
  'budget-finance':     '#16a34a',
  'transportation':     '#d97706',
  'zoning-land-use':   '#7c3aed',
  'public-safety':      '#dc2626',
  'policy-governance':  '#0d9488',
  'equity-inclusion':   '#db2777',
  'technology':         '#6366f1',
  'community-parks':    '#65a30d',
  'personnel':          '#92400e',
  'general':            '#71717a',
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

function CategoryPill({ slug }: { slug: string }) {
  const label = CATEGORY_LABELS[slug] ?? slug.replace(/-/g, ' ')
  const color = CATEGORY_COLORS[slug] ?? '#71717a'
  return (
    <Link
      href={`/categories/${slug}`}
      className="category-pill"
      style={{ '--cat-color': color } as React.CSSProperties}
    >
      {label}
    </Link>
  )
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
                  {item.primary_category && <CategoryPill slug={item.primary_category} />}
                  {item.secondary_tags?.slice(0, 2).map(t => (
                    <span key={t} className="chip chip-gray">{t}</span>
                  ))}
                </div>
                <div className="agenda-item-title">{item.title}</div>
                <div className="agenda-item-summary">{item.summary}</div>
                <div className="agenda-item-footer">
                  <span className="agenda-item-meta">
                    {item.board_slug && <span className="agenda-item-board">{BOARD_LABELS[item.board_slug] ?? item.board_slug}</span>}
                    {item.meeting_date && <span className="agenda-item-date">· {formatDate(String(item.meeting_date))}</span>}
                  </span>
                  <a href={`/meetings/${item.meeting_id}`} className="agenda-item-meeting-link">View meeting →</a>
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
