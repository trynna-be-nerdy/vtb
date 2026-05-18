import { Navbar } from '@/components/Navbar'
import { Sidebar } from '@/components/Sidebar'
import { Footer } from '@/components/Footer'
import { ScrollReveal } from '@/components/ScrollReveal'

export const revalidate = 3600

export default function AITransparencyPage() {
  return (
    <div className="site">
      <Navbar />
      <ScrollReveal />

      <div className="page-layout">
        <Sidebar />

        <div className="site-container">
          <div className="info-page">

            {/* ── Hero ── */}
            <div className="ai-hero" data-reveal>
              <div className="ai-hero-eyebrow">AI Transparency</div>
              <h1 className="ai-hero-title">
                Three prompts. Zero hallucinations.<br />
                Every word traced to an official source.
              </h1>
              <p className="ai-hero-sub">
                View the Board uses a purpose-built AI pipeline to turn dense government PDFs
                into plain English — automatically, every time a new meeting is published.
                Here's exactly how it works.
              </p>
            </div>

            {/* ── Why Gemma ── */}
            <div className="info-section ai-why-section" data-reveal>
              <div className="info-eyebrow">The model</div>
              <h2 className="info-title">Why Gemma 4</h2>
              <p className="info-body" style={{ marginBottom: 20 }}>
                Gemma 4 is Google DeepMind's most capable open-weights model — the same research
                lineage as Gemini, made available for anyone to run. We chose it for three specific reasons:
              </p>
              <div className="ai-why-grid">
                <div className="ai-why-card">
                  <div className="ai-why-icon">🔒</div>
                  <div className="ai-why-label">Fully private</div>
                  <div className="ai-why-desc">
                    The model runs on local hardware. Loudoun County meeting documents never leave
                    the machine — no cloud API, no data sharing, no third-party processing.
                  </div>
                </div>
                <div className="ai-why-card">
                  <div className="ai-why-icon">⚡</div>
                  <div className="ai-why-label">Structured output</div>
                  <div className="ai-why-desc">
                    Gemma 4 supports constrained JSON generation natively — meaning it can be forced
                    to return machine-readable data instead of free-form prose. No regex parsing, no
                    guessing, no hallucinated structure.
                  </div>
                </div>
                <div className="ai-why-card">
                  <div className="ai-why-icon">🧪</div>
                  <div className="ai-why-label">Open and auditable</div>
                  <div className="ai-why-desc">
                    Open weights means the model's behavior is reproducible and inspectable. Any
                    researcher can verify that the model isn't injecting bias — or swap it out
                    entirely if a better one emerges.
                  </div>
                </div>
                <div className="ai-why-card">
                  <div className="ai-why-icon">🏛️</div>
                  <div className="ai-why-label">Trained for comprehension</div>
                  <div className="ai-why-desc">
                    Government documents are a specific genre — procedural language, legal references,
                    fiscal notation. Gemma 4's broad training corpus includes regulatory and legislative
                    text, making it unusually fluent in this domain.
                  </div>
                </div>
              </div>
            </div>

            {/* ── Pipeline flow ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">The pipeline</div>
              <h2 className="info-title">From PDF to plain English in three steps</h2>
              <p className="info-body" style={{ marginBottom: 24 }}>
                Every time a new meeting is published by Loudoun County or LCPS, the same
                deterministic pipeline runs. No human edits the output. The three prompts
                are chained — each one builds on the last.
              </p>

              {/* Step 1 */}
              <div className="ai-step" data-reveal>
                <div className="ai-step-header">
                  <div className="ai-step-num">01</div>
                  <div className="ai-step-meta">
                    <div className="ai-step-label">Rewrite</div>
                    <div className="ai-step-sub">Runs once per agenda item chunk (~2,000 characters)</div>
                  </div>
                </div>
                <p className="ai-step-desc">
                  Each section of the agenda is passed individually. The model is instructed to
                  act as a plain-English rewriter — extracting only what was decided, what happens
                  next, and what the numbers were. It returns structured JSON, never prose.
                </p>
                <div className="ai-step-output">
                  <div className="ai-output-label">Output fields</div>
                  <div className="ai-output-chips">
                    <span className="ai-chip">title <span className="ai-chip-note">≤ 10 words</span></span>
                    <span className="ai-chip">summary <span className="ai-chip-note">2–4 sentences</span></span>
                    <span className="ai-chip">decisions[ ]</span>
                    <span className="ai-chip">action_items[ ]</span>
                    <span className="ai-chip">amounts[ ]</span>
                    <span className="ai-chip">vote_tallies[ ]</span>
                    <span className="ai-chip">dates[ ]</span>
                    <span className="ai-chip">schools[ ]</span>
                  </div>
                </div>
                <div className="ai-step-rule">
                  <span className="ai-rule-icon">⚠</span>
                  Vote tallies, dollar figures, and school names are copied verbatim from the source — the
                  model is explicitly instructed not to paraphrase these.
                </div>
              </div>

              {/* Step 2 */}
              <div className="ai-step" data-reveal>
                <div className="ai-step-header">
                  <div className="ai-step-num">02</div>
                  <div className="ai-step-meta">
                    <div className="ai-step-label">Classify</div>
                    <div className="ai-step-sub">Runs on the plain-English summary — not the raw PDF</div>
                  </div>
                </div>
                <p className="ai-step-desc">
                  The plain-English summary from Step 1 is classified — deliberately not the raw
                  bureaucratic text. Classifying human-readable language gives the model
                  better signal about intent rather than procedural phrasing. The output is
                  constrained to exactly 12 valid category slugs.
                </p>
                <div className="ai-step-output">
                  <div className="ai-output-label">Output fields</div>
                  <div className="ai-output-chips">
                    <span className="ai-chip">primary_category <span className="ai-chip-note">1 of 12</span></span>
                    <span className="ai-chip">secondary_tags[ ]</span>
                    <span className="ai-chip">urgency <span className="ai-chip-note">routine / notable / significant</span></span>
                    <span className="ai-chip">fiscal_impact <span className="ai-chip-note">boolean</span></span>
                    <span className="ai-chip">affects_schools[ ]</span>
                  </div>
                </div>
                <div className="ai-categories-row">
                  {['Budget & Finance','Schools & Education','Zoning & Land Use','Transportation',
                    'Public Safety','Policy & Governance','School Construction','Equity & Inclusion',
                    'Technology','Community & Parks','Personnel','General'].map(c => (
                    <span key={c} className="ai-cat-chip">{c}</span>
                  ))}
                </div>
              </div>

              {/* Step 3 */}
              <div className="ai-step" data-reveal>
                <div className="ai-step-header">
                  <div className="ai-step-num">03</div>
                  <div className="ai-step-meta">
                    <div className="ai-step-label">Synthesize</div>
                    <div className="ai-step-sub">Runs once per meeting — after all items are processed</div>
                  </div>
                </div>
                <p className="ai-step-desc">
                  All item summaries from Step 1 are concatenated and sent in a single pass.
                  The model produces a meeting-level narrative, surfaces the three most significant
                  decisions, and calculates the total fiscal footprint. This is the overview you
                  see at the top of every meeting page.
                </p>
                <div className="ai-step-output">
                  <div className="ai-output-label">Output fields</div>
                  <div className="ai-output-chips">
                    <span className="ai-chip">meeting_overview <span className="ai-chip-note">3–5 sentences</span></span>
                    <span className="ai-chip">top_decisions[ ] <span className="ai-chip-note">max 3</span></span>
                    <span className="ai-chip">fiscal_total <span className="ai-chip-note">or null</span></span>
                    <span className="ai-chip">next_meeting_notes</span>
                  </div>
                </div>
              </div>
            </div>

            {/* ── Validation ── */}
            <div className="info-section ai-validation-section" data-reveal>
              <div className="info-eyebrow">Reliability</div>
              <h2 className="info-title">What happens when the AI is wrong</h2>
              <p className="info-body" style={{ marginBottom: 20 }}>
                Every response is validated against a strict schema before it's written to the database.
                If a field is missing, the wrong type, or the JSON is malformed — the prompt is
                retried automatically with a correction instruction.
              </p>
              <div className="ai-stats-row">
                <div className="ai-stat-card">
                  <div className="ai-stat-value">~8%</div>
                  <div className="ai-stat-label">First-attempt failure rate</div>
                  <div className="ai-stat-sub">Mostly minor JSON formatting issues</div>
                </div>
                <div className="ai-stat-card">
                  <div className="ai-stat-value">&lt;1%</div>
                  <div className="ai-stat-label">Post-retry failure rate</div>
                  <div className="ai-stat-sub">Items that fail all retries are flagged, not published</div>
                </div>
                <div className="ai-stat-card">
                  <div className="ai-stat-value">2×</div>
                  <div className="ai-stat-label">Max retries per prompt</div>
                  <div className="ai-stat-sub">Each retry includes the specific error reason</div>
                </div>
              </div>
            </div>

            {/* ── Boundaries ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Hard limits</div>
              <h2 className="info-title">What this AI will never do</h2>
              <div className="ai-limits-list">
                <div className="ai-limit-item">
                  <span className="ai-limit-icon">✕</span>
                  <div>
                    <strong>Browse the internet or access live systems.</strong>{' '}
                    The model only sees text from the official source PDF — nothing else.
                  </div>
                </div>
                <div className="ai-limit-item">
                  <span className="ai-limit-icon">✕</span>
                  <div>
                    <strong>Form or express opinions.</strong>{' '}
                    The prompts contain no framing that would lead to opinion generation.
                    The model is asked to extract and restate, not evaluate.
                  </div>
                </div>
                <div className="ai-limit-item">
                  <span className="ai-limit-icon">✕</span>
                  <div>
                    <strong>Paraphrase numbers or vote results.</strong>{' '}
                    Dollar amounts, vote tallies, and dates are extracted verbatim.
                    If a document says "$6,812,000" the output says "$6,812,000".
                  </div>
                </div>
                <div className="ai-limit-item">
                  <span className="ai-limit-icon">✕</span>
                  <div>
                    <strong>Publish unverified output.</strong>{' '}
                    Items that fail schema validation after retries are marked as pending
                    and excluded from public display until they can be reviewed.
                  </div>
                </div>
              </div>
              <div className="ai-source-callout">
                Every AI-generated summary on this site links directly to its official source document.
                You can verify any claim in under 10 seconds.
              </div>
            </div>

          </div>
        </div>
      </div>

      <Footer />
    </div>
  )
}
