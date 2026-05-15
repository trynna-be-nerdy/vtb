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
      if (currentY > lastY.current && currentY > 60) {
        nav!.classList.add('hidden')
      } else {
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
          View the Board
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
