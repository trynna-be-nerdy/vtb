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
      {/* DaisyUI navbar layout inside existing .nav-inner container */}
      <div className="nav-inner">
        <div className="navbar-start" style={{ flex: 'none' }}>
          <Link href="/" className="nav-logo">
            View the Board
          </Link>
        </div>

        {/* DaisyUI btn-ghost gives subtle hover ripple and focus ring */}
        <div className="navbar-end" style={{ flex: 'none' }}>
          <Link
            href="/search"
            className="btn btn-ghost btn-sm"
            style={{
              borderRadius: 20,
              fontSize: 12,
              color: 'var(--color-text-secondary)',
              background: 'var(--color-background-secondary)',
              border: '0.5px solid var(--color-border-tertiary)',
              fontWeight: 400,
              letterSpacing: 0,
              height: 'auto',
              padding: '5px 14px',
              minHeight: 'unset',
            }}
          >
            Search by board, topic, or keyword
          </Link>
        </div>
      </div>
    </nav>
  )
}
