'use client'

import { useWsContext } from './ws-provider'

export function useJobProgress() {
  return useWsContext()
}
