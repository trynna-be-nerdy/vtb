export function OfficialSources() {
  return (
    <div>
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
    </div>
  )
}
