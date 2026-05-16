import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'

export const revalidate = 3600

export default function DataSourcesPage() {
  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          <div className="info-page">

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Data Sources</div>
              <h1 className="info-title">Where the data comes from</h1>
              <div className="info-body">
                <p>
                  All content on View the Board is derived exclusively from official public records published by
                  Loudoun County Government and Loudoun County Public Schools. No content is invented or inferred
                  beyond what appears in the source documents.
                </p>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Primary sources</div>
              <div className="info-body">
                <table className="info-table">
                  <thead>
                    <tr><th>Source</th><th>URL</th><th>Boards covered</th></tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Loudoun County Meeting Portal</strong></td>
                      <td><a href="https://loudoun.gov/meetings" target="_blank" rel="noopener noreferrer">loudoun.gov/meetings</a></td>
                      <td>Board of Supervisors, Planning Commission, Advisory Boards</td>
                    </tr>
                    <tr>
                      <td><strong>LCPS BoardDocs</strong></td>
                      <td><a href="https://lcps.org/boarddocs" target="_blank" rel="noopener noreferrer">lcps.org/boarddocs</a></td>
                      <td>LCPS School Board</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Data pipeline</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>How documents are collected</h2>
              <div className="info-body">
                <p>
                  Scrapers run every hour and check both portals for newly published agenda packets and minutes.
                  Each document URL is SHA-256 hashed to prevent duplicate processing.
                </p>
                <p>
                  Documents are downloaded as PDFs and text is extracted using <strong>pdfplumber</strong>.
                  A boilerplate filter removes repeating headers and footers before the text is chunked by
                  agenda item boundaries.
                </p>
                <p>
                  All data is stored in a PostgreSQL database with full-text search indexing (PostgreSQL
                  <code> tsvector</code>) and served through a Redis-cached API.
                </p>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Accuracy & limitations</div>
              <div className="info-body">
                <p>
                  <strong>What we guarantee:</strong> every summary is linked to the official source PDF so you
                  can verify any claim in seconds.
                </p>
                <p>
                  <strong>What we don't guarantee:</strong> AI-generated summaries may miss nuance, misstate
                  technical details, or omit information that wasn't clearly stated in the agenda text. Vote
                  counts and dollar figures are extracted but should be verified against official minutes.
                </p>
                <p>
                  If you spot an error, please <a href="/contact">contact us</a>.
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
