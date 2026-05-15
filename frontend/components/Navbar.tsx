'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'

export function Navbar() {
  const navRef   = useRef<HTMLElement>(null)
  const lastY    = useRef(0)
  const ticking  = useRef(false)
  const isHidden = useRef(false)

  useEffect(() => {
    const nav = navRef.current
    if (!nav) return

    function handleScroll() {
      const currentY   = window.scrollY
      const scrollingDown = currentY > lastY.current

      // Shadow appears once the user has scrolled even a little
      if (currentY > 8) {
        nav!.classList.add('scrolled')
      } else {
        nav!.classList.remove('scrolled')
      }

      if (scrollingDown && currentY > 80 && !isHidden.current) {
        // Hide: fast ease-in — user is reading, get out of the way quickly
        nav!.style.transition = 'top 0.18s cubic-bezier(0.4, 0, 1, 1)'
        nav!.classList.add('hidden')
        isHidden.current = true
      } else if (!scrollingDown && isHidden.current) {
        // Reveal: spring overshoot — feels lively, not jarring
        nav!.style.transition = 'top 0.42s cubic-bezier(0.34, 1.56, 0.64, 1)'
        nav!.classList.remove('hidden')
        isHidden.current = false
      }

      lastY.current  = currentY
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
        <Link href="/" className="nav-logo">
          View the <span className="nav-logo-red">Board</span>
          {/* Live pulse dot */}
          <span className="nav-live-dot" aria-hidden="true" />
        </Link>

        <Link href="/search" className="search-pill">
          Search by board, topic, or keyword
        </Link>
      </div>
    </nav>
  )
}
