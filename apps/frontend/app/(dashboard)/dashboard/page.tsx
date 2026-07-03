import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { Video, Scissors, Star, Zap } from 'lucide-react'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const firstName = user.user_metadata?.full_name?.split(' ')[0] ?? 'usuário'

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Olá, {firstName} 👋</h1>
        <p className="text-muted-foreground">
          Pronto para criar seus próximos cortes virais?
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Projetos criados"
          value="0"
          description="Nenhum projeto ainda"
          icon={Video}
        />
        <StatsCard
          title="Clips gerados"
          value="0"
          description="Aguardando primeiro upload"
          icon={Scissors}
        />
        <StatsCard
          title="Score médio"
          value="—"
          description="Virality score"
          icon={Star}
        />
        <StatsCard
          title="Créditos restantes"
          value="3"
          description="Plano Gratuito"
          icon={Zap}
        />
      </div>

      <div className="rounded-xl border bg-card p-8 text-center">
        <Video className="mx-auto mb-4 size-12 text-muted-foreground/40" />
        <h2 className="text-lg font-semibold">Nenhum projeto ainda</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Faça upload do seu primeiro vídeo para começar
        </p>
        <a
          href="/upload"
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          <Zap className="size-4" />
          Criar primeiro projeto
        </a>
      </div>
    </div>
  )
}
