'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

export interface DecisionGroup {
  meetingDate: string
  meetingTitle: string
  decisions: string[]
  totalItems: number
}

export function DecisionsAccordion({
  items,
  accentColor,
}: {
  items: DecisionGroup[]
  accentColor: string
}) {
  const [openIdx, setOpenIdx] = useState<number | null>(null)

  if (items.length === 0) return null

  return (
    <div className="fb-accordion">
      {items.map((group, i) => {
        const isOpen = openIdx === i
        return (
          <div key={i} className="fb-accordion-item">
            <button
              className="fb-accordion-trigger"
              onClick={() => setOpenIdx(isOpen ? null : i)}
              aria-expanded={isOpen}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <span className="fb-accordion-trigger-label">Key decisions</span>
                <span style={{ fontSize: 12, color: 'var(--color-text-primary)', fontWeight: 400 }}>
                  {group.meetingDate} — {group.meetingTitle}
                </span>
                <span
                  style={{
                    fontSize: 10,
                    fontWeight: 600,
                    padding: '1px 7px',
                    borderRadius: 9999,
                    background: 'var(--color-background-tertiary)',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  {group.decisions.length}
                </span>
              </div>
              <ChevronDown
                size={15}
                className={`fb-accordion-chevron ${isOpen ? 'open' : ''}`}
                aria-hidden
              />
            </button>

            <div className={`fb-accordion-body ${isOpen ? 'open' : ''}`}>
              <div className="fb-accordion-content">
                <ul className="fb-decision-list">
                  {group.decisions.map((d, j) => (
                    <li key={j} className="fb-decision-item">
                      {/* Dot uses the board's accent colour — set via inline style so it's always correct */}
                      <span
                        className="fb-decision-dot"
                        style={{ background: accentColor }}
                      />
                      <span>{d}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
