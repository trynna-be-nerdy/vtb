'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'

export function Navbar() {
  const navRef = useRef<HTMLElement>(null)
  const lastY = useRef(0)
  const ticking = useRef(false)
  // Track how many px the user has scrolled in the current direction
  const directionDelta = useRef(0)

  useEffect(() => {
    const nav = navRef.current
    if (!nav) return

    function handleScroll() {
      const currentY = window.scrollY
      const delta = currentY - lastY.current

      // Accumulate movement in the current direction; reset on reversal
      if (Math.sign(delta) !== Math.sign(directionDelta.current)) {
        directionDelta.current = 0
      }
      directionDelta.current += delta

      // Only hide after scrolling down 10 px past the fold; only show after scrolling up 6 px
      if (directionDelta.current > 10 && currentY > 80) {
        nav!.classList.add('hidden')
      } else if (directionDelta.current < -6) {
        nav!.classList.remove('hidden')
      }

      lastY.current = currentY
      ticking.current = false
    }

    function onScroll() {
      if (!ticking.current) {
        requestAnimationFrame(handleScroll)
        ticking.current = true
      }
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <nav ref={navRef} className="nav" id="navbar">
      <div className="nav-inner">
        <Link href="/" className="nav-logo">
          View the <span style={{ color: '#c0392b' }}>Board</span>
        </Link>
        {/* search-pill keeps its own hover; DaisyUI btn was removed because its
            inline-style overrides block .search-pill:hover from applying */}
        <Link href="/search" className="search-pill">
          Search by board, topic, or keyword
        </Link>
      </div>
    </nav>
  )
}
