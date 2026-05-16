'use client'

import { useEffect, useRef, useState } from 'react'
import Link from 'next/link'

// ≤ 5-word rotating taglines — each shown for 2.8 s
const TAGLINES = [
  'AI summaries · county boards',
  'Budget · Zoning · Schools',
  'LCPS · Supervisors · Planning',
  'Board meetings, plain English',
  'Public safety · land use',
]

function RotatingTagline() {
  const [idx, setIdx]       = useState(0)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const interval = setInterval(() => {
      // Fade out → swap text → fade in
      setVisible(false)
      setTimeout(() => {
        setIdx(i => (i + 1) % TAGLINES.length)
        setVisible(true)
      }, 350)
    }, 2800)
    return () => clearInterval(interval)
  }, [])

  return (
    <span
      className="nav-tagline"
      style={{ opacity: visible ? 1 : 0, transform: visible ? 'none' : 'translateY(4px)' }}
    >
      {TAGLINES[idx]}
    </span>
  )
}

export function Navbar() {
  const navRef   = useRef<HTMLElement>(null)
  const lastY    = useRef(0)
  const ticking  = useRef(false)
  const isHidden = useRef(false)

  useEffect(() => {
    const nav = navRef.current
    if (!nav) return

    function handleScroll() {
      const currentY      = window.scrollY
      const scrollingDown = currentY > lastY.current

      if (currentY > 8) {
        nav!.classList.add('scrolled')
      } else {
        nav!.classList.remove('scrolled')
      }

      if (scrollingDown && currentY > 80 && !isHidden.current) {
        nav!.style.transition = 'top 0.18s cubic-bezier(0.4, 0, 1, 1)'
        nav!.classList.add('hidden')
        isHidden.current = true
      } else if (!scrollingDown && isHidden.current) {
        nav!.style.transition = 'top 0.42s cubic-bezier(0.34, 1.56, 0.64, 1)'
        nav!.classList.remove('hidden')
        isHidden.current = false
      }

      lastY.current   = currentY
      ticking.current = false
    }

    function onScroll() {
      if (!ticking.current) {
        ticking.current = true
        requestAnimationFrame(handleScroll)
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav ref={navRef} className="nav" id="navbar">
      <div className="nav-inner">
        {/* Left: wordmark */}
        <Link href="/" className="nav-logo">
          View the <span className="nav-logo-red">Board</span>
          <span className="nav-live-dot" aria-hidden="true" />
        </Link>

        {/* Center: rotating 5-word tagline */}
        <RotatingTagline />

        {/* Right: search pill */}
        <Link href="/search" className="search-pill">
          Search by board, topic, or keyword
        </Link>
      </div>
    </nav>
  )
}
