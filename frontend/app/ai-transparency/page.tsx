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

            {/* ── Intro ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">AI Transparency</div>
              <h1 className="info-title">Three prompts. Every word traced to an official source.</h1>
              <div className="info-body">
                <p>
                  View the Board uses a purpose-built AI pipeline to turn dense government PDFs into
                  plain English — automatically, every time a new meeting is published. This page
                  explains exactly what the model does, why we chose it, and what it is never allowed to do.
                </p>
              </div>
            </div>

            {/* ── Why Gemma ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">The model</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Why Gemma 4</h2>
              <div className="info-body">
                <p>
                  Gemma 4 is Google DeepMind's most capable open-weights model — the same research
                  lineage as Gemini, made available for anyone to run and inspect. We chose it for
                  four specific reasons:
                </p>
                <table className="info-table">
                  <thead>
                    <tr>
                      <th>Reason</th>
                      <th>Why it matters here</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td><strong>Fully private</strong></td>
                      <td>The model runs on local hardware. Loudoun County meeting documents never leave the machine — no cloud API, no data sharing, no third-party processing.</td>
                    </tr>
                    <tr>
                      <td><strong>Structured output</strong></td>
                      <td>Gemma 4 supports constrained JSON generation natively, meaning it can be forced to return machine-readable data instead of free-form prose. No regex parsing, no hallucinated structure.</td>
                    </tr>
                    <tr>
                      <td><strong>Open and auditable</strong></td>
                      <td>Open weights means the model's behavior is reproducible and inspectable. Any researcher can verify the model isn't injecting bias — or swap it out if a better one emerges.</td>
                    </tr>
                    <tr>
                      <td><strong>Domain fluency</strong></td>
                      <td>Government documents are a specific genre — procedural language, legal references, fiscal notation. Gemma 4's broad training corpus includes regulatory and legislative text, making it unusually fluent in this domain.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ── Step 1 ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Step 1 of 3</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Rewrite — plain English from bureaucratic text</h2>
              <div className="info-body">
                <p>
                  Each agenda item chunk (max ~2,000 characters) is passed individually. The model acts
                  as a plain-English rewriter — extracting only what was decided, what happens next,
                  and what the numbers were. It returns structured JSON, never prose. This step runs
                  once per agenda item.
                </p>
                <table className="info-table">
                  <thead>
                    <tr><th>Output field</th><th>Constraint</th></tr>
                  </thead>
                  <tbody>
                    <tr><td><code>title</code></td><td>Maximum 10 words, plain English</td></tr>
                    <tr><td><code>summary</code></td><td>2–4 sentences, general adult audience, no jargon</td></tr>
                    <tr><td><code>decisions[ ]</code></td><td>Each decision or vote in plain language</td></tr>
                    <tr><td><code>action_items[ ]</code></td><td>Next steps and follow-up actions</td></tr>
                    <tr><td><code>amounts[ ]</code></td><td>Copied verbatim — not paraphrased</td></tr>
                    <tr><td><code>vote_tallies[ ]</code></td><td>Copied verbatim — e.g. "7-2 approved"</td></tr>
                    <tr><td><code>dates[ ]</code></td><td>Specific dates mentioned in the document</td></tr>
                    <tr><td><code>schools[ ]</code></td><td>School names mentioned verbatim</td></tr>
                  </tbody>
                </table>
                <p>
                  Vote tallies, dollar figures, and school names are copied verbatim from the source — the model is explicitly instructed not to paraphrase these.
                </p>
              </div>
            </div>

            {/* ── Step 2 ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Step 2 of 3</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Classify — category, urgency, fiscal flag</h2>
              <div className="info-body">
                <p>
                  The plain-English summary from Step 1 is classified — deliberately not the raw
                  bureaucratic text. Classifying human-readable language gives the model better
                  signal about intent rather than procedural phrasing. The output is constrained
                  to exactly 12 valid category slugs. This step runs once per agenda item, after Step 1.
                </p>
                <table className="info-table">
                  <thead>
                    <tr><th>Output field</th><th>Constraint</th></tr>
                  </thead>
                  <tbody>
                    <tr><td><code>primary_category</code></td><td>Exactly one of 12 slugs listed below</td></tr>
                    <tr><td><code>secondary_tags[ ]</code></td><td>Specific sub-topic tags for searchability</td></tr>
                    <tr><td><code>urgency</code></td><td>One of: <strong>routine</strong> / <strong>notable</strong> / <strong>significant</strong></td></tr>
                    <tr><td><code>fiscal_impact</code></td><td>Boolean — true only if a dollar amount is involved</td></tr>
                    <tr><td><code>affects_schools[ ]</code></td><td>School names if the item directly impacts a school</td></tr>
                  </tbody>
                </table>
                <p>
                  The 12 valid categories are: <strong>Budget &amp; Finance</strong>, Schools &amp; Education,
                  School Construction, Transportation, Zoning &amp; Land Use, Public Safety,
                  Policy &amp; Governance, Equity &amp; Inclusion, Technology, Community &amp; Parks,
                  Personnel, and General. If the model returns any other value, the item fails validation
                  and retries.
                </p>
              </div>
            </div>

            {/* ── Step 3 ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Step 3 of 3</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Synthesize — meeting-level overview</h2>
              <div className="info-body">
                <p>
                  After all agenda items are processed, all item summaries are concatenated and sent in
                  a single pass. The model produces a meeting-level narrative, surfaces the three most
                  significant decisions, and calculates the total fiscal footprint. This step runs
                  once per meeting — not once per item — keeping processing proportional to
                  meetings rather than agenda size.
                </p>
                <table className="info-table">
                  <thead>
                    <tr><th>Output field</th><th>Constraint</th></tr>
                  </thead>
                  <tbody>
                    <tr><td><code>meeting_overview</code></td><td>3–5 sentence narrative of the full meeting</td></tr>
                    <tr><td><code>top_decisions[ ]</code></td><td>Top 3 most significant decisions only</td></tr>
                    <tr><td><code>fiscal_total</code></td><td>Total dollar amount across all fiscal items, or null</td></tr>
                    <tr><td><code>next_meeting_notes</code></td><td>Any upcoming dates or agenda items flagged in the meeting</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* ── Validation ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Reliability</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>Validation and retry logic</h2>
              <div className="info-body">
                <p>
                  Every response is validated against a strict schema before it's written to the
                  database. If a field is missing, the wrong type, or the JSON is malformed — the
                  prompt is retried automatically with a correction instruction that includes the
                  specific error reason.
                </p>
                <table className="info-table">
                  <thead>
                    <tr><th>Metric</th><th>Value</th></tr>
                  </thead>
                  <tbody>
                    <tr><td>First-attempt failure rate</td><td>~8% — mostly minor JSON formatting issues</td></tr>
                    <tr><td>Post-retry failure rate</td><td>&lt;1% — items that fail all retries are not published</td></tr>
                    <tr><td>Max retries per prompt</td><td>2× — each retry includes the specific validation error</td></tr>
                  </tbody>
                </table>
                <p>
                  Items that fail all retries are marked as <strong>pending</strong> and excluded
                  from public display until they can be reviewed. Nothing is published without
                  passing schema validation.
                </p>
              </div>
            </div>

            {/* ── Hard limits ── */}
            <div className="info-section" data-reveal>
              <div className="info-eyebrow">Hard limits</div>
              <h2 className="info-title" style={{ fontSize: 18 }}>What this AI will never do</h2>
              <div className="info-body">
                <p><strong>Browse the internet or access live systems.</strong> The model only sees text from the official source PDF — nothing else is provided in the context window.</p>
                <p><strong>Form or express opinions.</strong> The prompts contain no framing that leads to opinion generation. The model is asked to extract and restate, not evaluate.</p>
                <p><strong>Paraphrase numbers or vote results.</strong> Dollar amounts, vote tallies, and dates are extracted verbatim. If a document says "$6,812,000" the output says "$6,812,000".</p>
                <p><strong>Publish unverified output.</strong> Items that fail schema validation after retries are flagged as pending and excluded from public display.</p>
                <p>
                  Every AI-generated summary on this site links directly to its official source
                  document. You can verify any claim in under 10 seconds.
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
