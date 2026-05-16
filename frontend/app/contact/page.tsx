import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'

export const revalidate = 3600

export default function ContactPage() {
  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          <div className="info-page">

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Contact</div>
              <h1 className="info-title">Get in touch</h1>
              <div className="info-body">
                <p>
                  View the Board is an independent civic project. We welcome feedback, error reports,
                  and questions about how the summaries are generated.
                </p>
              </div>

              <div className="info-contact-grid" style={{ marginTop: 20 }}>
                <a
                  href="mailto:srivastkris06@gmail.com"
                  className="info-contact-card"
                >
                  <div className="info-contact-label">Email</div>
                  <div className="info-contact-value">srivastkris06@gmail.com</div>
                </a>
                <a
                  href="https://github.com/trynna-be-nerdy"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="info-contact-card"
                >
                  <div className="info-contact-label">GitHub</div>
                  <div className="info-contact-value">trynna-be-nerdy</div>
                </a>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Reporting errors</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Found a mistake?</h2>
              <div className="info-body">
                <p>
                  If an AI-generated summary misrepresents an agenda item, please email us with:
                </p>
                <table className="info-table">
                  <tbody>
                    <tr><td><strong>Meeting title</strong></td><td>The board and date of the meeting</td></tr>
                    <tr><td><strong>Agenda item</strong></td><td>The item title as shown on the page</td></tr>
                    <tr><td><strong>The error</strong></td><td>What is wrong and what the correct information is</td></tr>
                    <tr><td><strong>Source</strong></td><td>A link to the official document if possible</td></tr>
                  </tbody>
                </table>
                <p style={{ marginTop: 12 }}>
                  We will review the report and manually correct or flag the item. Verified corrections are
                  applied within 48 hours.
                </p>
              </div>
            </div>

            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Not affiliated</div>
              <div className="info-body">
                <p>
                  View the Board is an independent project and is not affiliated with Loudoun County Government,
                  the Loudoun County Board of Supervisors, LCPS, or any government body. All data is sourced from
                  official public records and reproduced for informational purposes only.
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
