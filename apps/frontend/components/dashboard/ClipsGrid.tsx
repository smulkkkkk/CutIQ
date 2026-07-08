'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Scissors } from 'lucide-react'
import { useWsContext } from '@/notifications/ws-provider'
import { ClipCard } from './ClipCard'
import type { Clip } from '@/types'

export function ClipsGrid({ initialClips, projectId }: { initialClips: Clip[]; projectId: string }) {
  const router = useRouter()
  const { latestEvent } = useWsContext()

  useEffect(() => {
    if (latestEvent?.stage === 'analyzed' || latestEvent?.stage === 'completed') {
      router.refresh()
    }
  }, [latestEvent, router])

  if (initialClips.length === 0) {
    return (
      <div className="rounded-xl border bg-card p-8 text-center">
        <Scissors className="mx-auto mb-3 size-10 text-muted-foreground/40" />
        <p className="text-sm text-muted-foreground">
          Os clips aparecerão aqui após a análise com IA
        </p>
      </div>
    )
  }

  return (
    <div>
      <p className="mb-4 text-sm text-muted-foreground">
        {initialClips.length} clip{initialClips.length !== 1 ? 's' : ''} identificado{initialClips.length !== 1 ? 's' : ''}
      </p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {initialClips.map(clip => (
          <ClipCard key={clip.id} clip={clip} />
        ))}
      </div>
    </div>
  )
}
