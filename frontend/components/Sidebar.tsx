'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const BOARDS = [
  { slug: 'board-of-supervisors', label: 'Board of Supervisors', dot: 'dot-blue' },
  { slug: 'planning-commission',  label: 'Planning Commission',  dot: 'dot-teal' },
  { slug: 'lcps-school-board',    label: 'LCPS School Board',    dot: 'dot-amber' },
  { slug: 'advisory-boards',      label: 'Advisory Boards',      dot: 'dot-purple' },
]

const CATEGORIES = [
  { slug: 'budget-finance',    label: 'Budget & Finance' },
  { slug: 'schools-education', label: 'Schools & Education' },
  { slug: 'zoning-land-use',   label: 'Zoning & Land Use' },
  { slug: 'transportation',    label: 'Transportation' },
  { slug: 'public-safety',     label: 'Public Safety' },
  { slug: 'policy-governance', label: 'Policy & Governance' },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="sidebar">
      {/* Home */}
      <div className="sidebar-section">
        <Link
          href="/"
          className={`sidebar-item ${pathname === '/' ? 'sidebar-item-active' : ''}`}
        >
          <span className="sidebar-home-icon">◈</span>
          Today
        </Link>
        <Link
          href="/calendar"
          className={`sidebar-item ${pathname === '/calendar' ? 'sidebar-item-active' : ''}`}
        >
          <span className="sidebar-home-icon">⊡</span>
          Calendar
        </Link>
        <Link
          href="/search"
          className={`sidebar-item ${pathname === '/search' ? 'sidebar-item-active' : ''}`}
        >
          <span className="sidebar-home-icon">⊙</span>
          Search
        </Link>
      </div>

      <div className="sidebar-divider" />

      {/* Boards */}
      <div className="sidebar-section">
        <div className="sidebar-section-label">Boards</div>
        {BOARDS.map(board => (
          <Link
            key={board.slug}
            href={`/boards/${board.slug}`}
            className={`sidebar-item ${pathname === `/boards/${board.slug}` ? 'sidebar-item-active' : ''}`}
          >
            <span className={`dot ${board.dot}`} style={{ width: 7, height: 7, flexShrink: 0 }} />
            {board.label}
          </Link>
        ))}
      </div>

      <div className="sidebar-divider" />

      {/* Categories */}
      <div className="sidebar-section">
        <div className="sidebar-section-label">Categories</div>
        {CATEGORIES.map(cat => (
          <Link
            key={cat.slug}
            href={`/categories/${cat.slug}`}
            className={`sidebar-item ${pathname === `/categories/${cat.slug}` ? 'sidebar-item-active' : ''}`}
          >
            {cat.label}
          </Link>
        ))}
      </div>

      <div className="sidebar-divider" />

      {/* Footer links */}
      <div className="sidebar-section sidebar-footer-links">
        <Link href="/about"           className="sidebar-item sidebar-item-sm">About</Link>
        <Link href="/data-sources"    className="sidebar-item sidebar-item-sm">Data sources</Link>
        <Link href="/ai-transparency" className="sidebar-item sidebar-item-sm">AI transparency</Link>
      </div>
    </aside>
  )
}
