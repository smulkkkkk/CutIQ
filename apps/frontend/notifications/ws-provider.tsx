'use client'

import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { createClient } from '@/lib/supabase/client'
import type { JobProgressEvent } from '@/types'

interface WsContextValue {
  events: JobProgressEvent[]
  latestEvent: JobProgressEvent | null
  isConnected: boolean
}

const WsContext = createContext<WsContextValue>({
  events: [],
  latestEvent: null,
  isConnected: false,
})

const BASE_WS_URL =
  (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000')
    .replace(/^http/, 'ws')

interface WsProviderProps {
  projectId: string
  children: ReactNode
}

export function WsProvider({ projectId, children }: WsProviderProps) {
  const [events, setEvents] = useState<JobProgressEvent[]>([])
  const [latestEvent, setLatestEvent] = useState<JobProgressEvent | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    let ws: WebSocket
    let cancelled = false

    async function connect() {
      const supabase = createClient()
      const { data: { session } } = await supabase.auth.getSession()
      if (!session?.access_token || cancelled) return

      ws = new WebSocket(`${BASE_WS_URL}/ws/${projectId}?token=${session.access_token}`)
      wsRef.current = ws

      ws.onopen = () => !cancelled && setIsConnected(true)
      ws.onclose = () => !cancelled && setIsConnected(false)
      ws.onerror = () => !cancelled && setIsConnected(false)
      ws.onmessage = (e) => {
        if (cancelled) return
        try {
          const event = JSON.parse(e.data) as JobProgressEvent
          setLatestEvent(event)
          setEvents((prev) => [...prev, event])
        } catch {}
      }
    }

    connect()

    return () => {
      cancelled = true
      ws?.close()
      setIsConnected(false)
    }
  }, [projectId])

  return (
    <WsContext.Provider value={{ events, latestEvent, isConnected }}>
      {children}
    </WsContext.Provider>
  )
}

export function useWsContext() {
  return useContext(WsContext)
}
