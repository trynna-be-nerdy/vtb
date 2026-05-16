import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'

export const revalidate = 3600

export default function AboutPage() {
  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          <div className="info-page">

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">About</div>
              <h1 className="info-title">View the Board</h1>
              <div className="info-body">
                <p>
                  View the Board makes Loudoun County government accessible to everyone. Every Board of Supervisors,
                  Planning Commission, LCPS School Board, and Advisory Board meeting is automatically processed into
                  plain-English summaries the same day it's published.
                </p>
                <p>
                  Local government is the layer of democracy that most directly affects daily life — school funding,
                  zoning decisions, road projects, public safety budgets. Yet most residents never engage because the
                  materials are dense PDFs written in bureaucratic language, scattered across multiple portals.
                </p>
                <p>
                  View the Board closes that gap: every agenda item is rewritten, categorised, and made searchable
                  — powered by <strong>Gemma 4</strong> running locally via Ollama, with every summary linked back
                  to its official source document.
                </p>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">How it works</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>From PDF to plain English in three steps</h2>
              <div className="info-body">
                <table className="info-table">
                  <thead>
                    <tr>
                      <th>Step</th>
                      <th>What happens</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>1. Discover</strong></td>
                      <td>Scrapers check loudoun.gov/meetings and lcps.org/boarddocs for new agenda PDFs every hour.</td>
                    </tr>
                    <tr>
                      <td><strong>2. Process</strong></td>
                      <td>Each PDF is extracted with pdfplumber, chunked by agenda item, and sent to Gemma 4 for rewriting and classification.</td>
                    </tr>
                    <tr>
                      <td><strong>3. Publish</strong></td>
                      <td>Summaries are stored in PostgreSQL and served through a Redis-cached FastAPI backend. Real-time updates arrive via WebSocket.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Coverage</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Boards we track</h2>
              <div className="info-body">
                <table className="info-table">
                  <thead><tr><th>Board</th><th>Source</th></tr></thead>
                  <tbody>
                    <tr><td><strong>Board of Supervisors</strong></td><td>loudoun.gov/meetings</td></tr>
                    <tr><td><strong>Planning Commission</strong></td><td>loudoun.gov/meetings</td></tr>
                    <tr><td><strong>LCPS School Board</strong></td><td>lcps.org/boarddocs</td></tr>
                    <tr><td><strong>Advisory Boards & Committees</strong></td><td>loudoun.gov/meetings</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Disclaimer</div>
              <div className="info-body">
                <p>
                  View the Board is an independent project and is <strong>not affiliated with Loudoun County
                  Government or LCPS</strong>. Summaries are AI-generated from official public records and are
                  provided for informational purposes only. Always verify important information against the
                  official source documents linked on each page.
                </p>
              </div>
            </div>

          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}
