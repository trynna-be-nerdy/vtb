'use client'

import Link from 'next/link'

const LINKS = [
  { href: '/about',           label: 'About' },
  { href: '/data-sources',    label: 'Data sources' },
  { href: '/ai-transparency', label: 'AI transparency' },
]

export function PageInfoWidget() {
  return (
    <div className="page-info-widget" aria-label="Site info">
      {LINKS.map(({ href, label }) => (
        <Link key={href} href={href} className="page-info-link">
          {label}
        </Link>
      ))}
    </div>
  )
}
