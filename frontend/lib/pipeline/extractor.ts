/**
 * PDF text extraction — port of backend/pipeline/pdf_extractor.py
 * Uses pdf-parse (Node.js) instead of pdfplumber (Python).
 * Returns the full text as a single block (page boundaries not tracked).
 */

import pdfParse from 'pdf-parse'

export interface ExtractedText {
  text: string
  numPages: number
}

export async function extractText(pdfBuffer: Buffer): Promise<ExtractedText> {
  const data = await pdfParse(pdfBuffer)
  const cleaned = stripBoilerplate(data.text, data.numpages)
  return { text: cleaned, numPages: data.numpages }
}

function stripBoilerplate(text: string, numPages: number): string {
  if (numPages < 3) return text

  const lines = text.split('\n')
  const lineCounts = new Map<string, number>()
  for (const line of lines) {
    const stripped = line.trim()
    if (stripped) {
      lineCounts.set(stripped, (lineCounts.get(stripped) ?? 0) + 1)
    }
  }

  const threshold = Math.max(2, Math.floor(numPages * 0.6))
  const boilerplate = new Set<string>()
  for (const [line, count] of lineCounts) {
    if (count >= threshold) boilerplate.add(line)
  }

  if (boilerplate.size === 0) return text
  return lines
    .filter(l => !boilerplate.has(l.trim()))
    .join('\n')
}
