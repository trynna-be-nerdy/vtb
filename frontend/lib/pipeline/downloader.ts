/**
 * PDF downloader — port of backend/pipeline/downloader.py
 */

import { createHash } from 'crypto'
import { tmpdir } from 'os'
import { join } from 'path'
import { readFile, writeFile, access } from 'fs/promises'
import { BROWSER_HEADERS } from './types'

const MAX_RETRIES = 3
const TIMEOUT_MS = 60_000

function tempPath(url: string): string {
  const name = createHash('sha256').update(url).digest('hex').slice(0, 16)
  return join(tmpdir(), `${name}.pdf`)
}

export async function downloadPdf(url: string): Promise<Buffer> {
  const dest = tempPath(url)

  // Return cached file if it exists
  try {
    await access(dest)
    return readFile(dest)
  } catch {
    // not cached
  }

  let lastError: unknown
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const resp = await fetch(url, {
        headers: { ...BROWSER_HEADERS, Accept: 'application/pdf,*/*' },
        signal: AbortSignal.timeout(TIMEOUT_MS),
        redirect: 'follow',
      })
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

      const contentType = resp.headers.get('content-type') ?? ''
      if (!contentType.includes('application/pdf') && !url.toLowerCase().endsWith('.pdf')) {
        throw new Error(`Expected application/pdf, got '${contentType}'`)
      }

      const buf = Buffer.from(await resp.arrayBuffer())
      await writeFile(dest, buf)
      return buf
    } catch (err) {
      lastError = err
      if (attempt < MAX_RETRIES - 1) {
        await new Promise(r => setTimeout(r, 2 ** attempt * 1000))
      }
    }
  }
  throw new Error(`Failed to download ${url} after ${MAX_RETRIES} attempts: ${lastError}`)
}
