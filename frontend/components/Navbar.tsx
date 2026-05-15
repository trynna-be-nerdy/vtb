'use client'

import { useEffect, useRef } from 'react'
import Link from 'next/link'

export function Navbar() {
  const navRef = useRef<HTMLElement>(null)
  const lastY = useRef(0)
  const ticking = useRef(false)

  useEffect(() => {
    const nav = navRef.current
    if (!nav) return

    function handleScroll() {
      const currentY = window.scrollY
      const scrollingDown = currentY > lastY.current

      if (scrollingDown && currentY > 80) {
        nav.classList.add('hidden')
      } else if (!scrollingDown) {
        nav.classList.remove('hidden')
      }

      lastY.current = currentY
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
