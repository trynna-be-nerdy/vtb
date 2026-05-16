'use client'

import { useEffect, useRef, useState } from 'react'

export type SSEStatus = 'connecting' | 'connected' | 'disconnected'

export interface LiveEvent {
  type: 'new_item' | 'ping'
  meeting_id?: number
  item_id?: number
  title?: string
  category?: string
  timestamp?: string
}

const BASE_DELAY_MS = 2_000
const MAX_DELAY_MS  = 60_000
const BACKOFF_FACTOR = 1.8

export function useSSE(url: string = '/api/updates') {
  const [status, setStatus]           = useState<SSEStatus>('connecting')
  const [latestEvent, setLatestEvent] = useState<LiveEvent | null>(null)
  const esRef     = useRef<EventSource | null>(null)
  const retryRef  = useRef<ReturnType<typeof setTimeout> | null>(null)
  const delayRef  = useRef(BASE_DELAY_MS)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true

    function connect() {
      if (!mountedRef.current) return
      setStatus('connecting')

      const es = new EventSource(url)
      esRef.current = es

      es.onopen = () => {
        if (!mountedRef.current) return
        setStatus('connected')
        delayRef.current = BASE_DELAY_MS  // reset backoff on success
      }

      es.onmessage = (e) => {
        if (!mountedRef.current) return
        try {
          const data: LiveEvent = JSON.parse(e.data)
          if (data.type === 'ping') return
          setLatestEvent(data)
        } catch {
          // ignore malformed messages
        }
      }

      es.onerror = () => {
        es.close()
        if (!mountedRef.current) return
        setStatus('disconnected')
        const delay = Math.min(delayRef.current, MAX_DELAY_MS)
        delayRef.current = Math.round(delay * BACKOFF_FACTOR)
        retryRef.current = setTimeout(connect, delay)
      }
    }

    connect()

    return () => {
      mountedRef.current = false
      esRef.current?.close()
      if (retryRef.current) clearTimeout(retryRef.current)
    }
  }, [url])

  return { status, latestEvent }
}
