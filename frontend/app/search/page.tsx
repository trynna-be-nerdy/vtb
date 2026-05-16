'use client'

import { useState, useEffect } from 'react'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { SearchInput } from '@/components/SearchInput'
import type { SearchResponse, SearchResult } from '@/lib/types'

const BOARD_LABELS: Record<string, string> = {
  'board-of-supervisors': 'Board of Supervisors',
  'planning-commission':  'Planning Commission',
  'lcps-school-board':    'LCPS School Board',
  'advisory-boards':      'Advisory Boards',
}

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

/** Wrap matched query words in <mark> tags for inline highlighting */
function buildHighlightedHtml(text: string, query: string): string {
  if (!query || query.length < 2) return escapeHtml(text)
  const words = query.trim().split(/\s+/).filter(w => w.length > 1)
  if (!words.length) return escapeHtml(text)
  const escaped = words.map(w => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
  const re = new RegExp(`(${escaped.join('|')})`, 'gi')
  return escapeHtml(text).replace(re, '<mark class="search-mark">$1</mark>')
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
}

function ResultCard({ result, query }: { result: SearchResult; query: string }) {
  const titleHtml   = buildHighlightedHtml(result.title, query)
  const snippet     = result.summary.slice(0, 240) + (result.summary.length > 240 ? '…' : '')
  const summaryHtml = buildHighlightedHtml(snippet, query)

  const urgencyBadge =
    result.urgency === 'Significant' ? 'badge badge-error badge-sm'   :
    result.urgency === 'Notable'     ? 'badge badge-warning badge-sm' :
                                       'badge badge-ghost badge-sm'

  return (
    <a
      href={`/meetings/${result.meeting_id}`}
      className="search-result-card"
      style={{ textDecoration: 'none' }}
    >
      <div className="search-result-top">
        <span className="search-result-board">
          {BOARD_LABELS[result.board_slug] ?? result.board_slug}
          {' · '}
          {formatDate(result.meeting_date)}
        </span>
        <span className={urgencyBadge} style={{ fontSize: 9, padding: '1px 7px', flexShrink: 0 }}>
          {result.urgency}
        </span>
      </div>

      <div
        className="search-result-title"
        dangerouslySetInnerHTML={{ __html: titleHtml }}
      />
      <div
        className="search-result-summary"
        dangerouslySetInnerHTML={{ __html: summaryHtml }}
      />

      <div className="search-result-tags">
        {result.primary_category && (
          <span className="chip chip-gray" style={{ fontSize: 10 }}>
            {result.primary_category.replace(/-/g, ' ')}
          </span>
        )}
        {result.fiscal_impact && (
          <span className="chip chip-green" style={{ fontSize: 10 }}>$ Fiscal</span>
        )}
        {result.secondary_tags?.slice(0, 2).map(tag => (
          <span key={tag} className="chip chip-gray" style={{ fontSize: 10 }}>{tag}</span>
        ))}
      </div>
    </a>
  )
}

const SUGGESTIONS = ['rezoning', 'school budget', 'transportation', 'data center', 'fiscal impact', 'public safety']

export default function SearchPage() {
  const [query, setQuery]               = useState('')
  const [debouncedQuery, setDebounced]  = useState('')
  const [results, setResults]           = useState<SearchResult[] | null>(null)
  const [loading, setLoading]           = useState(false)
  const [error, setError]               = useState<string | null>(null)
  const [total, setTotal]               = useState(0)

  // 400 ms debounce
  useEffect(() => {
    const t = setTimeout(() => setDebounced(query), 400)
    return () => clearTimeout(t)
  }, [query])

  // Fetch whenever debounced query changes
  useEffect(() => {
    if (debouncedQuery.length < 2) {
      setResults(null)
      setTotal(0)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(null)

    fetch(`/api/search?q=${encodeURIComponent(debouncedQuery)}&limit=20`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<SearchResponse>
      })
      .then(data => {
        if (cancelled) return
        setResults(data.results ?? [])
        setTotal(data.pagination?.total ?? 0)
      })
      .catch(() => {
        if (!cancelled) setError('Search failed — please try again.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => { cancelled = true }
  }, [debouncedQuery])

  const hasResults = results !== null && results.length > 0
  const isEmpty    = results !== null && results.length === 0 && !loading

  return (
    <div className="site">
      <Navbar />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          {/* ── Page header ── */}
          <div className="search-page-header">
            <h1 className="search-page-title">Search</h1>
            <p className="search-page-sub">
              Full-text search across all board meetings, agenda items, and decisions.
            </p>
          </div>

          {/* ── Search input ── */}
          <div className="search-page-input-wrap">
            <SearchInput
              value={query}
              onChange={setQuery}
              loading={loading && debouncedQuery.length >= 2}
            />
          </div>

          {/* Results count */}
          {hasResults && !loading && (
            <div className="search-results-meta">
              {total} result{total !== 1 ? 's' : ''} for &ldquo;{debouncedQuery}&rdquo;
            </div>
          )}

          {/* Error */}
          {error && <div className="search-error">{error}</div>}

          {/* Empty state */}
          {isEmpty && (
            <div className="search-empty">
              <div className="search-empty-icon">⊘</div>
              <div className="search-empty-title">No results for &ldquo;{debouncedQuery}&rdquo;</div>
              <div className="search-empty-sub">
                Try a different keyword, or browse by board or category from the sidebar.
              </div>
            </div>
          )}

          {/* Initial prompt with suggestions */}
          {results === null && !loading && (
            <div className="search-prompt">
              <div className="search-prompt-label">Try searching for</div>
              <div className="search-suggestions">
                {SUGGESTIONS.map(s => (
                  <button
                    key={s}
                    className="search-suggestion"
                    onClick={() => setQuery(s)}
                    type="button"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Results list */}
          {hasResults && (
            <div className="search-results-list">
              {results.map(r => (
                <ResultCard key={r.id} result={r} query={debouncedQuery} />
              ))}
            </div>
          )}

          <div style={{ height: 48 }} />
        </div>
      </div>
    </div>
  )
}
