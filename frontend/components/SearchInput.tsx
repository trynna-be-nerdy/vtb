'use client'

import { useRef, useEffect } from 'react'
import { Search, X } from 'lucide-react'

interface SearchInputProps {
  value: string
  onChange: (val: string) => void
  placeholder?: string
  loading?: boolean
}

export function SearchInput({
  value,
  onChange,
  placeholder = 'Search by board, topic, or keyword…',
  loading = false,
}: SearchInputProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  // Autofocus on mount
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  return (
    <div className="search-input-wrapper">
      <div className="search-input-icon" aria-hidden>
        {loading ? (
          <div className="search-spinner" />
        ) : (
          <Search size={15} />
        )}
      </div>
      <input
        ref={inputRef}
        type="search"
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        className="search-input"
        autoComplete="off"
        spellCheck={false}
      />
      {value && (
        <button
          className="search-clear-btn"
          onClick={() => onChange('')}
          aria-label="Clear search"
          type="button"
        >
          <X size={13} />
        </button>
      )}
    </div>
  )
}
