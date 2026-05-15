import { fetchBoardMeetings, fetchRecentMeetings, fetchHealth } from '@/lib/api'
import { BOARD_CONFIGS } from '@/lib/types'
import { Navbar } from '@/components/Navbar'
import { IntroSection } from '@/components/IntroSection'
import { BoardSection } from '@/components/BoardSection'

export const revalidate = 60

export default async function HomePage() {
  // Fetch all boards in parallel with ISR caching
  const [
    supervisorMeetings,
    planningMeetings,
    schoolMeetings,
    advisoryMeetings,
    recentMeetings,
    health,
  ] = await Promise.all([
    fetchBoardMeetings('board-of-supervisors', 3),
    fetchBoardMeetings('planning-commission', 3),
    fetchBoardMeetings('lcps-school-board', 3),
    fetchBoardMeetings('advisory-boards', 4),
    fetchRecentMeetings(9),
    fetchHealth(),
  ])

  const boardData = [supervisorMeetings, planningMeetings, schoolMeetings, advisoryMeetings]

  return (
    <div className="site">
      <Navbar />

      <div className="site-container">
      <IntroSection recentMeetings={recentMeetings} />

      <div className="main">
        {BOARD_CONFIGS.map((board, i) => (
          <BoardSection
            key={board.slug}
            dot={board.dot}
            title={board.title}
            meta={board.meta}
            meetings={boardData[i]}
            isAdvisory={board.isAdvisory}
            slug={board.slug}
          />
        ))}
      </div>

      {/* Official sources + newsletter */}
      <div className="content-section">
        <div className="content-divider">
          <div className="content-divider-line" />
          <div className="content-divider-label">Official sources</div>
          <div className="content-divider-line" />
        </div>

        <div className="resources-grid">
          <a
            href="https://loudoun.gov/meetings"
            target="_blank"
            rel="noopener noreferrer"
            className="resource-card"
            style={{ textDecoration: 'none' }}
          >
            <div className="resource-eyebrow">Official source</div>
            <div className="resource-title">Loudoun County meeting portal</div>
            <div className="resource-desc">
              Access agendas, meeting packets, minutes, and vote records directly from the county — the primary source for all View the Board summaries.
            </div>
            <div className="resource-cta">loudoun.gov/meetings →</div>
          </a>
          <a
            href="https://lcps.org/boarddocs"
            target="_blank"
            rel="noopener noreferrer"
            className="resource-card"
            style={{ textDecoration: 'none' }}
          >
            <div className="resource-eyebrow">Official source</div>
            <div className="resource-title">LCPS BoardDocs meeting portal</div>
            <div className="resource-desc">
              View original school board agendas, attachments, and archived webcast recordings published separately through LCPS.
            </div>
            <div className="resource-cta">lcps.org/boarddocs →</div>
          </a>
          <div className="resource-card">
            <div className="resource-eyebrow">Resident guide</div>
            <div className="resource-title">How to speak at a board meeting</div>
            <div className="resource-desc">
              Step-by-step guide to signing up for public comment at any Loudoun County board — supervisors, school board, planning commission, or advisory body.
            </div>
            <div className="resource-cta">View guide →</div>
          </div>
        </div>

        {/* Pipeline status / about blurb */}
        <div
          style={{
            background: 'var(--color-background-primary)',
            border: '0.5px solid var(--color-border-tertiary)',
            borderRadius: 'var(--border-radius-lg)',
            padding: '20px 24px',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: 32,
          }}
        >
          <div
            style={{
              fontSize: 13,
              color: 'var(--color-text-secondary)',
              lineHeight: 1.6,
              maxWidth: 560,
            }}
          >
            View the Board converts official county and LCPS meeting records into plain-English summaries, structured action logs, and decision timelines — powered by AI, linked to every official source.
          </div>
          <div
            style={{
              flexShrink: 0,
              textAlign: 'right',
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
            }}
          >
            {health && (
              <>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginBottom: 2 }}>Last updated</div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-primary)' }}>
                    {health.last_pipeline_run
                      ? new Date(health.last_pipeline_run).toLocaleString('en-US', {
                          month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
                        })
                      : 'Not yet run'}
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 11, color: 'var(--color-text-secondary)', marginBottom: 2 }}>Items this month</div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: 'var(--color-text-primary)' }}>
                    {health.items_this_month} agenda items
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="content-divider">
          <div className="content-divider-line" />
          <div className="content-divider-label">Stay informed</div>
          <div className="content-divider-line" />
        </div>

        <NewsletterForm />
      </div>

      </div>{/* end site-container */}

      <div className="site-footer">
        <div className="footer-links">
          <a href="/about" className="footer-link-item" style={{ textDecoration: 'none' }}>About</a>
          <a href="/data-sources" className="footer-link-item" style={{ textDecoration: 'none' }}>Data sources</a>
          <a href="/ai-transparency" className="footer-link-item" style={{ textDecoration: 'none' }}>AI transparency</a>
          <a href="/contact" className="footer-link-item" style={{ textDecoration: 'none' }}>Contact</a>
        </div>
        <div className="footer-copy">
          View the Board · Not affiliated with Loudoun County Government · Summaries generated by AI from official public documents
        </div>
      </div>
    </div>
  )
}

function NewsletterForm() {
  return (
    <div className="newsletter">
      <div>
        <div className="newsletter-title">Get a weekly digest in your inbox</div>
        <div className="newsletter-sub">
          Every Sunday — the most significant decisions from all five Loudoun County boards, in plain English. No spam, unsubscribe anytime.
        </div>
      </div>
      <form className="newsletter-form" action="/api/subscribe" method="POST">
        <input
          className="newsletter-input"
          type="email"
          name="email"
          placeholder="your@email.com"
          required
        />
        <button className="newsletter-btn" type="submit">
          Subscribe
        </button>
      </form>
    </div>
  )
}
