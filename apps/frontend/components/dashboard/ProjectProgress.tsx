'use client'

import { useJobProgress } from '@/notifications/use-job-progress'
import { CheckCircle, Loader2, XCircle } from 'lucide-react'

const STAGE_LABELS: Record<string, string> = {
  transcribing: 'Transcrevendo...',
  transcribed: 'Transcrição concluída',
  analyzing: 'Analisando com IA...',
  analyzed: 'Análise concluída',
  rendering: 'Renderizando clip...',
  clip_ready: 'Clip pronto!',
  completed: 'Processamento concluído',
  failed: 'Falha no processamento',
}

export function ProjectProgress() {
  const { latestEvent, isConnected } = useJobProgress()

  if (!latestEvent && !isConnected) {
    return (
      <div className="rounded-xl border bg-card p-6 text-center text-sm text-muted-foreground">
        Aguardando início do processamento...
      </div>
    )
  }

  const stage = latestEvent?.stage
  const isFailed = stage === 'failed'
  const isCompleted = stage === 'completed'

  return (
    <div className="rounded-xl border bg-card p-6 space-y-4">
      <div className="flex items-center gap-3">
        {isCompleted ? (
          <CheckCircle className="size-5 text-green-500" />
        ) : isFailed ? (
          <XCircle className="size-5 text-destructive" />
        ) : (
          <Loader2 className="size-5 animate-spin text-primary" />
        )}
        <p className="font-medium">
          {stage ? STAGE_LABELS[stage] ?? stage : 'Conectando...'}
        </p>
      </div>

      {latestEvent?.progress !== undefined && !isCompleted && !isFailed && (
        <div className="space-y-1">
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-500"
              style={{ width: `${latestEvent.progress}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground text-right">{latestEvent.progress}%</p>
        </div>
      )}

      {isFailed && latestEvent?.message && (
        <p className="text-sm text-destructive">{latestEvent.message}</p>
      )}

      {stage === 'analyzed' && latestEvent?.clips_count !== undefined && (
        <p className="text-sm text-muted-foreground">
          {latestEvent.clips_count} clips identificados
        </p>
      )}
    </div>
  )
}
