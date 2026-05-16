import { getMeetings, getHealth } from '@/lib/data'
import { BOARD_CONFIGS } from '@/lib/types'
import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { IntroSection } from '@/components/IntroSection'
import { BoardSection } from '@/components/BoardSection'
import { ScrollReveal } from '@/components/ScrollReveal'
import { OfficialSources } from '@/components/OfficialSources'
import { AboutStats } from '@/components/AboutStats'
import { Newsletter } from '@/components/Newsletter'
import { Footer } from '@/components/Footer'
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

          <div className="content-section">
            <OfficialSources />
            <AboutStats health={health as { items_this_month?: number; last_pipeline_run?: string | null } | null} />

            <div className="content-divider">
              <div className="content-divider-line" />
              <div className="content-divider-label">Stay informed</div>
              <div className="content-divider-line" />
            </div>

            <Newsletter />
          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}
