/**
 * Deduplication — port of backend/pipeline/deduplicator.py
 * Uses direct DB functions from lib/data.ts
 */

import { filterNewDocumentUrls } from '@/lib/data'
import type { DocumentInfo } from './types'

export async function filterNewDocuments(documents: DocumentInfo[]): Promise<DocumentInfo[]> {
  if (documents.length === 0) return []

  const pdfUrls = documents.map(d => d.pdf_url)
  const alreadyProcessed = await filterNewDocumentUrls(pdfUrls)

  const newDocs = documents.filter(d => !alreadyProcessed.has(d.pdf_url))
  console.log(
    `[deduplicator] ${documents.length} total, ${newDocs.length} new, ${documents.length - newDocs.length} skipped`,
  )
  return newDocs
}
