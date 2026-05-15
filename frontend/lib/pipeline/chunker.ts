/**
 * Agenda item chunker — port of backend/pipeline/chunker.py
 */

const MAX_CHUNK_CHARS = 2_000
const CONTEXT_OVERLAP = 200

const HEADER_PATTERNS: RegExp[] = [
  /(?:Item|ITEM)\s*\d+\.?[A-Z]?/i,
  /(?:Action|ACTION)\s+(?:Item|ITEM)/i,
  /(?:Consent|CONSENT)\s+(?:Agenda|AGENDA)/i,
  /(?:PUBLIC|CITIZEN)\s+(?:HEARING|COMMENT)/i,
]

export interface Chunk {
  text: string
  detectedHeader: string | null
  charCount: number
}

export function chunkText(fullText: string): Chunk[] {
  if (!fullText.trim()) return []

  const lines = fullText.split('\n')
  const segments = splitOnHeaders(lines)
  const chunks: Chunk[] = []

  for (const [header, segLines] of segments) {
    const segText = segLines.join('\n')
    if (segText.length <= MAX_CHUNK_CHARS) {
      chunks.push({ text: segText, detectedHeader: header, charCount: segText.length })
    } else {
      chunks.push(...splitOversized(segText, header))
    }
  }

  return chunks
}

function detectHeader(line: string): string | null {
  const stripped = line.trim()
  for (const pattern of HEADER_PATTERNS) {
    if (pattern.test(stripped)) return stripped
  }
  return null
}

function splitOnHeaders(lines: string[]): Array<[string | null, string[]]> {
  const segments: Array<[string | null, string[]]> = []
  let currentHeader: string | null = null
  let currentLines: string[] = []

  for (const line of lines) {
    const header = detectHeader(line)
    if (header !== null) {
      if (currentLines.length > 0) {
        segments.push([currentHeader, currentLines])
      }
      const context = trailingContext(currentLines)
      currentHeader = header
      currentLines = [...context, line]
    } else {
      currentLines.push(line)
    }
  }

  if (currentLines.length > 0) {
    segments.push([currentHeader, currentLines])
  }

  return segments
}

function trailingContext(lines: string[]): string[] {
  const result: string[] = []
  let total = 0
  for (let i = lines.length - 1; i >= 0; i--) {
    total += lines[i].length + 1
    result.unshift(lines[i])
    if (total >= CONTEXT_OVERLAP) break
  }
  return result
}

function splitOversized(text: string, header: string | null): Chunk[] {
  const pieces: Chunk[] = []
  let current = ''
  let isFirst = true

  for (const line of text.split('\n')) {
    if (current.length + line.length + 1 > MAX_CHUNK_CHARS && current) {
      const t = current.trimEnd()
      pieces.push({ text: t, detectedHeader: isFirst ? header : null, charCount: t.length })
      current = ''
      isFirst = false
    }
    current += (current ? '\n' : '') + line
  }

  if (current.trim()) {
    const t = current.trimEnd()
    pieces.push({ text: t, detectedHeader: isFirst ? header : null, charCount: t.length })
  }

  return pieces
}
