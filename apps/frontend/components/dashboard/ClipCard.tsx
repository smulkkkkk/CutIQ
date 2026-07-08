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
  return (
    <div className="rounded-xl border bg-card p-4 space-y-3 hover:border-primary/50 transition-colors">
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
        {clip.has_watermark && (
          <span className="text-xs text-muted-foreground">com marca d'água</span>
        )}
      </div>
    </div>
  )
}
