'use client'

import { useState } from 'react'
import { Download, Loader2 } from 'lucide-react'
import { api } from '@/lib/api/client'
import type { Clip } from '@/types'

function ScoreBadge({ score }: { score: number | null }) {
  if (score === null) return <span className="text-xs text-muted-foreground">—</span>
  const color =
    score >= 80 ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
    score >= 60 ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                  'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold ${color}`}>
      {score}
    </span>
  )
}

function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function ClipCard({ clip }: { clip: Clip }) {
  const [downloading, setDownloading] = useState(false)

  async function handleDownload() {
    setDownloading(true)
    try {
      const { download_url, filename } = await api.clips.download(clip.id)
      const a = document.createElement('a')
      a.href = download_url
      a.download = filename
      a.click()
    } finally {
      setDownloading(false)
    }
  }

  return (
    <div className="rounded-xl border bg-card overflow-hidden hover:border-primary/50 transition-colors">
      {clip.thumbnail_r2_key && (
        <div className="aspect-[9/16] max-h-40 w-full overflow-hidden bg-muted">
          <img
            src={`/api/clips/${clip.id}/thumbnail`}
            alt={clip.title ?? 'Clip thumbnail'}
            className="h-full w-full object-cover"
          />
        </div>
      )}

      <div className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <p className="font-medium text-sm leading-snug line-clamp-2">
            {clip.title ?? 'Clip sem título'}
          </p>
          <ScoreBadge score={clip.virality_score} />
        </div>

        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>{formatDuration(clip.duration)}</span>
          <span>·</span>
          <span>{clip.start_time.toFixed(1)}s → {clip.end_time.toFixed(1)}s</span>
        </div>

        {clip.virality_reasons && clip.virality_reasons.length > 0 && (
          <ul className="space-y-1">
            {clip.virality_reasons.map((reason, i) => (
              <li key={i} className="text-xs text-muted-foreground flex gap-1.5">
                <span className="text-primary mt-0.5">✦</span>
                {reason}
              </li>
            ))}
          </ul>
        )}

        <div className="flex items-center justify-between">
          <span className={`text-xs px-2 py-0.5 rounded-full border ${
            clip.status === 'ready' ? 'border-green-500/30 text-green-600' :
            clip.status === 'failed' ? 'border-red-500/30 text-red-600' :
            'border-muted text-muted-foreground'
          }`}>
            {clip.status === 'pending' ? 'Aguardando render' :
             clip.status === 'rendering' ? 'Renderizando...' :
             clip.status === 'ready' ? 'Pronto' : 'Falhou'}
          </span>

          {clip.status === 'ready' && (
            <button
              onClick={handleDownload}
              disabled={downloading}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-primary hover:text-primary/80 disabled:opacity-50 transition-colors"
            >
              {downloading ? (
                <Loader2 className="size-3.5 animate-spin" />
              ) : (
                <Download className="size-3.5" />
              )}
              Baixar
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
