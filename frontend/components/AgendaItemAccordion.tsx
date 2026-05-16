'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import type { AgendaItemDetail } from '@/lib/types'

const URGENCY_BADGE: Record<string, string> = {
  Significant: 'badge badge-error badge-sm',
  Notable:     'badge badge-warning badge-sm',
  Routine:     'badge badge-ghost badge-sm',
}

export function AgendaItemAccordion({ items }: { items: AgendaItemDetail[] }) {
  const [openIdx, setOpenIdx] = useState<number | null>(null)

  if (items.length === 0) {
    return <div className="empty-state">No agenda items found for this meeting.</div>
  }

  return (
    <div className="agenda-accordion">
      {items.map((item, i) => {
        const isOpen = openIdx === i
        const badgeCls = URGENCY_BADGE[item.urgency] ?? URGENCY_BADGE.Routine

        return (
          <div key={item.id} className="agenda-item">
            <button
              className="agenda-trigger"
              onClick={() => setOpenIdx(isOpen ? null : i)}
              aria-expanded={isOpen}
            >
              <div className="agenda-trigger-left">
                <span className={badgeCls} style={{ fontSize: 9, padding: '1px 7px', flexShrink: 0 }}>
                  {item.urgency}
                </span>
                <span className="agenda-trigger-title">{item.title}</span>
                {item.fiscal_impact && (
                  <span className="chip chip-green" style={{ fontSize: 9.5, flexShrink: 0 }}>$ Fiscal</span>
                )}
              </div>
              <ChevronDown
                size={14}
                className={`fb-accordion-chevron ${isOpen ? 'open' : ''}`}
                aria-hidden
              />
            </button>

            <div className={`agenda-body ${isOpen ? 'open' : ''}`}>
              <div className="agenda-content">
                {/* Summary */}
                <p className="agenda-summary">{item.summary}</p>

                {/* Decisions */}
                {item.decisions && item.decisions.length > 0 && (
                  <div className="agenda-block">
                    <div className="agenda-block-label">Decisions</div>
                    <ul className="agenda-list">
                      {item.decisions.map((d, j) => (
                        <li key={j} className="agenda-list-item">{d}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Action Items */}
                {item.action_items && item.action_items.length > 0 && (
                  <div className="agenda-block">
                    <div className="agenda-block-label">Action Items</div>
                    <ul className="agenda-list">
                      {item.action_items.map((a, j) => (
                        <li key={j} className="agenda-list-item">{a}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Footer: category chip, page ref, source PDF */}
                <div className="agenda-footer">
                  {item.primary_category && (
                    <span className="chip chip-gray" style={{ fontSize: 10 }}>
                      {item.primary_category.replace(/-/g, ' ')}
                    </span>
                  )}
                  {item.secondary_tags?.slice(0, 2).map(tag => (
                    <span key={tag} className="chip chip-gray" style={{ fontSize: 10 }}>{tag}</span>
                  ))}
                  {item.page_range && (
                    <span className="agenda-page-ref">Pages {item.page_range}</span>
                  )}
                  {item.source_pdf_url && (
                    <a
                      href={item.source_pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="agenda-pdf-link"
                    >
                      View source PDF →
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
