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

    // Initialise to current scroll position so page-load-mid-scroll doesn't flash
    lastY.current = window.scrollY

    function handleScroll() {
      const currentY      = window.scrollY
      const scrollingDown = currentY > lastY.current
      const delta         = Math.abs(currentY - lastY.current)

      // Only act on intentional scrolls (ignore tiny jitter)
      if (delta < 2) {
        ticking.current = false
        return
      }

      // Shadow once scrolled past top
      if (currentY > 4) {
        nav!.classList.add('scrolled')
      } else {
        nav!.classList.remove('scrolled')
      }

      // Hide on scroll down after 40 px; reveal on any scroll up
      if (scrollingDown && currentY > 40 && !isHidden.current) {
        nav!.style.transition = 'top 0.2s cubic-bezier(0.4, 0, 1, 1), opacity 0.2s ease, box-shadow 0.2s ease'
        nav!.classList.add('hidden')
        isHidden.current = true
      } else if (!scrollingDown && isHidden.current) {
        nav!.style.transition = 'top 0.38s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease, box-shadow 0.3s ease'
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

      </div>
    </nav>
  )
}
