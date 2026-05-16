'use client'

import { useEffect, useRef, useState } from 'react'
import { useSSE } from '@/hooks/useSSE'
import type { LiveEvent } from '@/hooks/useSSE'

const CATEGORY_LABELS: Record<string, string> = {
  'schools-education':   'Schools',
  'school-construction': 'Construction',
  'budget-finance':      'Budget',
  'transportation':      'Transportation',
  'zoning-land-use':     'Zoning',
  'public-safety':       'Public Safety',
  'policy-governance':   'Policy',
  'equity-inclusion':    'Equity',
  'technology':          'Technology',
  'community-parks':     'Community',
  'personnel':           'Personnel',
  'general':             'General',
}

interface Toast {
  id: number
  event: LiveEvent
}

let nextId = 1

export function LiveUpdateToast() {
  const { status, latestEvent } = useSSE()
  const [toasts, setToasts] = useState<Toast[]>([])
  const seenRef = useRef<Set<number>>(new Set())

  // Push a new toast whenever a new_item event arrives
  useEffect(() => {
    if (!latestEvent || latestEvent.type !== 'new_item') return
    const key = latestEvent.item_id ?? 0
    if (seenRef.current.has(key)) return
    seenRef.current.add(key)

    const id = nextId++
    setToasts(prev => [...prev, { id, event: latestEvent }])

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, 5_000)
  }, [latestEvent])

  function dismiss(id: number) {
    setToasts(prev => prev.filter(t => t.id !== id))
  }

  if (toasts.length === 0) return null

  return (
    <div className="toast-stack" aria-live="polite">
      {toasts.map(({ id, event }) => (
        <div key={id} className="toast-item">
          <div className="toast-top">
            <span className="toast-eyebrow">New agenda item</span>
            {event.category && (
              <span className="chip chip-teal" style={{ fontSize: 10 }}>
                {CATEGORY_LABELS[event.category] ?? event.category}
              </span>
            )}
            <button
              className="toast-close"
              onClick={() => dismiss(id)}
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
          <div className="toast-title">{event.title ?? 'New item published'}</div>
          {event.meeting_id && (
            <a href={`/meetings/${event.meeting_id}`} className="toast-link">
              View meeting →
            </a>
          )}
        </div>
      ))}
    </div>
  )
}
