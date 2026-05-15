/**
 * Pipeline runner — orchestrates scraping, extraction, LLM processing, and DB writes.
 * Port of the Python pipeline worker.
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
import type { DocumentInfo } from './types'

export async function runPipeline(): Promise<void> {
  const runId = await createPipelineRun()
  console.log(`[pipeline] Run ${runId} started`)
  await publishUpdate({ event: 'pipeline_started', run_id: runId })

  try {
    // 1. Discover documents from all sources
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

    // 2. Deduplicate
    const newDocs = await filterNewDocuments(allDocs)
    await updatePipelineRun(runId, {
      status: 'running',
      documents_found: allDocs.length,
    })

    let totalItemsCreated = 0

    // 3. Process each new document
    for (const doc of newDocs) {
      try {
        await processDocument(doc)
        totalItemsCreated++
        await publishUpdate({ event: 'document_processed', url: doc.url })
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

    console.log(`[pipeline] Run ${runId} completed — ${totalItemsCreated} meetings processed`)
    await publishUpdate({ event: 'pipeline_completed', run_id: runId, items_created: totalItemsCreated })
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err)
    console.error(`[pipeline] Run ${runId} failed:`, err)
    await updatePipelineRun(runId, { status: 'failed', error_message: msg })
    await publishUpdate({ event: 'pipeline_failed', run_id: runId, error: msg })
    throw err
  }
}

async function processDocument(doc: DocumentInfo): Promise<void> {
  console.log(`[pipeline] Processing: ${doc.title}`)
  await upsertSeenDocument(doc.pdf_url, '', 'processing')

  // Download PDF
  const pdfBuffer = await downloadPdf(doc.pdf_url)
  const sha256 = createHash('sha256').update(pdfBuffer).digest('hex')

  // Extract text
  const { text } = await extractText(pdfBuffer)
  if (!text.trim()) {
    await upsertSeenDocument(doc.pdf_url, sha256, 'failed')
    throw new Error('PDF has no extractable text')
  }

  // Create/find meeting record
  const meetingId = await upsertMeeting({
    title: doc.title,
    board_slug: doc.board_type,
    meeting_date: doc.meeting_date,
    source_url: doc.url,
    source_pdf_url: doc.pdf_url,
  })

  // Chunk text and process each chunk with LLM
  const chunks = chunkText(text)
  const summaries: string[] = []
  let fiscalItems = 0

  for (const chunk of chunks) {
    if (!chunk.text.trim()) continue

    const [rewrite, classification] = await Promise.all([
      rewriteContent(chunk.text),
      Promise.resolve(null), // classify after rewrite
    ])

    const classify = await classifyContent(rewrite.summary)

    await insertAgendaItem({
      meeting_id: meetingId,
      title: rewrite.title,
      summary: rewrite.summary,
      decisions: rewrite.decisions,
      action_items: rewrite.action_items,
      key_figures: {
        amounts: rewrite.key_figures.amounts,
        vote_tallies: rewrite.key_figures.vote_tallies,
        dates: rewrite.key_figures.dates,
        schools: rewrite.key_figures.schools,
      },
      primary_category: classify.primary_category,
      secondary_tags: classify.secondary_tags,
      urgency: classify.urgency,
      fiscal_impact: classify.fiscal_impact,
      affects_schools: classify.affects_schools,
      source_pdf_url: doc.pdf_url,
    })

    summaries.push(rewrite.summary)
    if (classify.fiscal_impact) fiscalItems++
  }

  // Generate meeting-level overview (Prompt 3)
  if (summaries.length > 0) {
    const overview = await generateMeetingOverview(summaries)
    await finalizeMeeting(meetingId, overview, {
      total_items: summaries.length,
      fiscal_items: fiscalItems,
    })
  }

  await upsertSeenDocument(doc.pdf_url, sha256, 'completed')
  console.log(`[pipeline] Done: ${doc.title} (${summaries.length} items)`)
}
