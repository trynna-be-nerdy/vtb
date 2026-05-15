'use client'

import { useEffect } from 'react'

/**
 * Drop this anywhere in the tree — it attaches one IntersectionObserver
 * that watches every [data-reveal] element and adds .revealed when it enters
 * the viewport, triggering the CSS fade-up transition.
 */
export function ScrollReveal() {
  useEffect(() => {
    if (typeof window === 'undefined' || !('IntersectionObserver' in window)) return

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target as HTMLElement
            // Stagger siblings — find index among data-reveal siblings
            const siblings = Array.from(
              el.parentElement?.querySelectorAll('[data-reveal]') ?? []
            )
            const idx = siblings.indexOf(el)
            el.style.transitionDelay = `${idx * 60}ms`
            el.classList.add('revealed')
            observer.unobserve(el)
          }
        })
      },
      { threshold: 0.07, rootMargin: '0px 0px -32px 0px' }
    )

    document.querySelectorAll('[data-reveal]').forEach((el) => observer.observe(el))

    return () => observer.disconnect()
  }, [])

  return null
}
