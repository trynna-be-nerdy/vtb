'use client'

export function Newsletter() {
  return (
    <div className="newsletter">
      <div>
        <div className="newsletter-title">Get a weekly digest in your inbox</div>
        <div className="newsletter-sub">
          Every Sunday — the most significant decisions from all five Loudoun County boards, in plain English. No spam, unsubscribe anytime.
        </div>
      </div>
      <form action="/api/subscribe" method="POST">
        <div className="join">
          <input
            className="input input-bordered join-item"
            type="email"
            name="email"
            placeholder="your@email.com"
            required
            style={{
              fontSize: 13,
              height: 36,
              width: 210,
              borderColor: 'var(--color-border-secondary)',
              background: 'var(--color-background-secondary)',
              color: 'var(--color-text-primary)',
            }}
          />
          <button
            className="btn btn-neutral join-item"
            type="submit"
            style={{ fontSize: 13, height: 36, minHeight: 'unset', padding: '0 16px' }}
          >
            Subscribe
          </button>
        </div>
      </form>
    </div>
  )
}
