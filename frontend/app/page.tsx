import { getMeetings, getHealth } from '@/lib/data'
import { BOARD_CONFIGS } from '@/lib/types'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { IntroSection } from '@/components/IntroSection'
import { BoardSection } from '@/components/BoardSection'
import { ScrollReveal } from '@/components/ScrollReveal'
import type { MeetingCard } from '@/lib/types'

// Revalidate every 60 seconds (ISR)
export const revalidate = 60
// Force dynamic so DB calls don't run at build time without a DB
export const dynamic = 'force-dynamic'

export default async function HomePage() {
  // Fetch all boards + health in parallel directly from DB (no HTTP hop)
  const [
    supervisorMeetings,
    planningMeetings,
    schoolMeetings,
    advisoryMeetings,
    recentMeetingsData,
    health,
  ] = await Promise.all([
    getMeetings('board-of-supervisors', 1, 3).then(d => (d as { meetings: MeetingCard[] }).meetings).catch(() => [] as MeetingCard[]),
    getMeetings('planning-commission', 1, 3).then(d => (d as { meetings: MeetingCard[] }).meetings).catch(() => [] as MeetingCard[]),
    getMeetings('lcps-school-board', 1, 3).then(d => (d as { meetings: MeetingCard[] }).meetings).catch(() => [] as MeetingCard[]),
    getMeetings('advisory-boards', 1, 4).then(d => (d as { meetings: MeetingCard[] }).meetings).catch(() => [] as MeetingCard[]),
    getMeetings(null, 1, 9).then(d => (d as { meetings: MeetingCard[] }).meetings).catch(() => [] as MeetingCard[]),
    getHealth().catch(() => null),
  ])

  const boardData = [supervisorMeetings, planningMeetings, schoolMeetings, advisoryMeetings]

  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          <div className="intro-wrapper">
            <IntroSection recentMeetings={recentMeetingsData} />
          </div>

          <div className="main">
            {BOARD_CONFIGS.map((board, i) => (
              <div key={board.slug} data-reveal>
                <BoardSection
                  dot={board.dot}
                  title={board.title}
                  meta={board.meta}
                  meetings={boardData[i]}
                  isAdvisory={board.isAdvisory}
                  slug={board.slug}
                />
              </div>
            ))}
          </div>

          {/* Official sources + newsletter */}
          <div className="content-section">
          <div className="content-divider">
            <div className="content-divider-line" />
            <div className="content-divider-label">Official sources</div>
            <div className="content-divider-line" />
          </div>

          {/* Resource cards — card + card-bordered for DaisyUI structure, resource-card provides padding/layout */}
          <div className="resources-grid">
            <a
              href="https://loudoun.gov/meetings"
              target="_blank"
              rel="noopener noreferrer"
              className="card card-bordered resource-card"
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
              className="card card-bordered resource-card"
              style={{ textDecoration: 'none' }}
            >
              <div className="resource-eyebrow">Official source</div>
              <div className="resource-title">LCPS BoardDocs meeting portal</div>
              <div className="resource-desc">
                View original school board agendas, attachments, and archived webcast recordings published separately through LCPS.
              </div>
              <div className="resource-cta">lcps.org/boarddocs →</div>
            </a>
            <div className="card card-bordered resource-card">
              <div className="resource-eyebrow">Resident guide</div>
              <div className="resource-title">How to speak at a board meeting</div>
              <div className="resource-desc">
                Step-by-step guide to signing up for public comment at any Loudoun County board — supervisors, school board, planning commission, or advisory body.
              </div>
              <div className="resource-cta">View guide →</div>
            </div>
          </div>

          {/* About blurb + DaisyUI-style stats panel */}
          <div
            style={{
              background: 'var(--color-background-primary)',
              border: '0.5px solid var(--color-border-tertiary)',
              borderRadius: 'var(--border-radius-lg)',
              padding: '20px 24px',
            }}
          >
            <div
              style={{
                fontSize: 13,
                color: 'var(--color-text-secondary)',
                lineHeight: 1.6,
                marginBottom: health ? 16 : 0,
              }}
            >
              View the Board converts official county and LCPS meeting records into plain-English summaries, structured action logs, and decision timelines — powered by AI, linked to every official source.
            </div>

            {/* DaisyUI-inspired stats row */}
            {health && (
              <div className="vtb-stats">
                <div className="vtb-stat">
                  <div className="vtb-stat-title">Items This Month</div>
                  <div className="vtb-stat-value">
                    {(health as { items_this_month: number }).items_this_month}
                  </div>
                  <div className="vtb-stat-desc">Agenda items tracked</div>
                </div>
                <div className="vtb-stat">
                  <div className="vtb-stat-title">Queue Depth</div>
                  <div className="vtb-stat-value">
                    {(health as { queue_depth: number }).queue_depth ?? 0}
                  </div>
                  <div className="vtb-stat-desc">Pending documents</div>
                </div>
                <div className="vtb-stat">
                  <div className="vtb-stat-title">Last Pipeline Run</div>
                  <div className="vtb-stat-value" style={{ fontSize: 14 }}>
                    {(health as { last_pipeline_run: string | null }).last_pipeline_run
                      ? new Date((health as { last_pipeline_run: string }).last_pipeline_run).toLocaleString('en-US', {
                          month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
                        })
                      : '—'}
                  </div>
                  <div className="vtb-stat-live">Live</div>
                </div>
              </div>
            )}
          </div>

          <div className="content-divider">
            <div className="content-divider-line" />
            <div className="content-divider-label">Stay informed</div>
            <div className="content-divider-line" />
          </div>

          <NewsletterForm />
          </div>
        </div>
      </div>

      <div className="site-footer">
        <div className="site-footer-inner">
          {/* Left — equal weight to right spacer */}
          <div className="footer-left">
            <a href="/contact" className="footer-link-item" style={{ textDecoration: 'none' }}>Contact</a>
          </div>
          {/* Center — copyright */}
          <div className="footer-copy">
            View the Board · Not affiliated with Loudoun County Government · AI-generated summaries from official public records
          </div>
          {/* Right — mirrors left for balance */}
          <div className="footer-right" />
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
      {/* DaisyUI join — groups input + button into a single seamless pill */}
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
