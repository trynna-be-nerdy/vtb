/**
 * Pipeline runner — orchestrates scraping, extraction, LLM processing, and DB writes.
 * Port of the Python pipeline worker. Equivalent of backend/pipeline/worker.py + processor.py.
 */

import { createHash } from 'crypto'
import {
  createPipelineRun,
  updatePipelineRun,
  upsertSeenDocument,
  upsertMeeting,
  insertAgendaItem,
  finalizeMeeting,
} from '@/lib/data'
import { publishUpdate } from '@/lib/redis'
import { rewriteContent, classifyContent, generateMeetingOverview } from '@/lib/llm'
import { discoverLoudounDocuments } from './scraper-loudoun'
import { discoverLcpsDocuments } from './scraper-lcps'
import { downloadPdf } from './downloader'
import { extractText } from './extractor'
import { chunkText } from './chunker'
import { filterNewDocuments } from './deduplicator'
import { validateAgendaItem } from './validator'
import type { DocumentInfo } from './types'

export async function runPipeline(): Promise<void> {
  const runId = await createPipelineRun()
  console.log(`[pipeline] Run ${runId} started`)
  await publishUpdate({ event: 'pipeline_started', run_id: runId })

  try {
    // Step 1: Discover documents from all sources in parallel
    const [loudounDocs, lcpsDocs] = await Promise.all([
      discoverLoudounDocuments().catch(err => {
        console.warn(`[pipeline] Loudoun scraper failed: ${err}`)
        return [] as DocumentInfo[]
      }),
      discoverLcpsDocuments().catch(err => {
        console.warn(`[pipeline] LCPS scraper failed: ${err}`)
        return [] as DocumentInfo[]
      }),
    ])

    const allDocs = [...loudounDocs, ...lcpsDocs]
    console.log(`[pipeline] Discovered ${allDocs.length} documents`)
    await publishUpdate({ event: 'discovered', count: allDocs.length })

    // Step 2: Deduplicate against seen_documents
    const newDocs = await filterNewDocuments(allDocs)
    await updatePipelineRun(runId, {
      status: 'running',
      documents_found: allDocs.length,
    })

    let totalItemsCreated = 0

    // Steps 3–11: Process each new document; errors per-document don't stop the run
    for (const doc of newDocs) {
      try {
        const itemsCreated = await processDocument(doc)
        totalItemsCreated += itemsCreated
        await publishUpdate({ event: 'document_processed', url: doc.url, items: itemsCreated })
      } catch (err) {
        console.error(`[pipeline] Failed to process ${doc.url}:`, err)
        await upsertSeenDocument(doc.pdf_url, '', 'failed')
      }
    }

    await updatePipelineRun(runId, {
      status: 'completed',
      documents_found: allDocs.length,
      documents_processed: newDocs.length,
      items_created: totalItemsCreated,
    })

    console.log(`[pipeline] Run ${runId} completed — ${totalItemsCreated} agenda items created`)
    await publishUpdate({ event: 'pipeline_completed', run_id: runId, items_created: totalItemsCreated })
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    console.error(`[pipeline] Run ${runId} failed:`, err)
    await updatePipelineRun(runId, { status: 'failed', error_message: msg })
    await publishUpdate({ event: 'pipeline_failed', run_id: runId, error: msg })
    throw err
  }
}

/** Returns number of agenda items successfully written. */
async function processDocument(doc: DocumentInfo): Promise<number> {
  console.log(`[pipeline] Processing: ${doc.title}`)
  await upsertSeenDocument(doc.pdf_url, '', 'processing')

  // Step 3: Download PDF
  const pdfBuffer = await downloadPdf(doc.pdf_url)
  const sha256 = createHash('sha256').update(pdfBuffer).digest('hex')

  // Step 4: Extract text
  const { text } = await extractText(pdfBuffer)
  if (!text.trim()) {
    await upsertSeenDocument(doc.pdf_url, sha256, 'failed')
    throw new Error('PDF has no extractable text')
  }

  // Step 5: Chunk into agenda-item-sized pieces
  const chunks = chunkText(text)

  // Create/find meeting record
  const meetingId = await upsertMeeting({
    title: doc.title,
    board_slug: doc.board_type,
    meeting_date: doc.meeting_date,
    source_url: doc.url,
    source_pdf_url: doc.pdf_url,
  })

  const summaries: string[] = []
  let fiscalItems = 0
  let itemsWritten = 0
  // Tracks normalised titles seen in this meeting for duplicate-detection (check #8)
  const seenTitles = new Set<string>()

  for (const chunk of chunks) {
    if (!chunk.text.trim()) continue

    // Step 6: Prompt 1 — content rewrite
    const rewrite = await rewriteContent(chunk.text)

    // Step 7: Prompt 2 — classification (uses the rewritten summary, not raw chunk)
    const classify = await classifyContent(rewrite.summary)

    // Step 8: Run 10 quality-validation checks before DB write
    const draft = {
      title:            rewrite.title,
      summary:          rewrite.summary,
      decisions:        rewrite.decisions,
      primary_category: classify.primary_category,
      urgency:          classify.urgency,
      key_figures:      rewrite.key_figures,
      source_pdf_url:   doc.pdf_url,
    }

    const validation = validateAgendaItem(draft, seenTitles)
    if (!validation.valid) {
      console.warn(`[pipeline] Skipping invalid item "${rewrite.title}":`, validation.errors)
      continue
    }

    // Step 9: Atomic PostgreSQL write — insert agenda item
    await insertAgendaItem({
      meeting_id:       meetingId,
      title:            rewrite.title,
      summary:          rewrite.summary,
      decisions:        rewrite.decisions,
      action_items:     rewrite.action_items,
      key_figures: {
        amounts:      rewrite.key_figures.amounts,
        vote_tallies: rewrite.key_figures.vote_tallies,
        dates:        rewrite.key_figures.dates,
        schools:      rewrite.key_figures.schools,
      },
      primary_category: classify.primary_category,
      secondary_tags:   classify.secondary_tags,
      urgency:          classify.urgency,
      fiscal_impact:    classify.fiscal_impact,
      affects_schools:  classify.affects_schools,
      source_pdf_url:   doc.pdf_url,
    })

    summaries.push(rewrite.summary)
    if (classify.fiscal_impact) fiscalItems++
    itemsWritten++
  }

  // Step 10: Prompt 3 — generate meeting-level overview from all item summaries
  if (summaries.length > 0) {
    const overview = await generateMeetingOverview(summaries)

    // Step 11: Update meeting record with overview
    await finalizeMeeting(meetingId, overview, {
      total_items:  summaries.length,
      fiscal_items: fiscalItems,
    })
  }

  await upsertSeenDocument(doc.pdf_url, sha256, 'completed')
  console.log(`[pipeline] Done: ${doc.title} — ${itemsWritten}/${chunks.length} items written`)
  return itemsWritten
}
