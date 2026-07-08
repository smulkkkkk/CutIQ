import { redirect } from 'next/navigation'
import { createClient } from '@/lib/supabase/server'
import { WsProvider } from '@/notifications/ws-provider'
import { ProjectProgress } from '@/components/dashboard/ProjectProgress'
import { ClipsGrid } from '@/components/dashboard/ClipsGrid'
import type { Metadata } from 'next'
import type { Clip } from '@/types'

export const metadata: Metadata = {
  title: 'Projeto — CutIQ',
}

interface Props {
  params: Promise<{ id: string }>
}

export default async function ProjectPage({ params }: Props) {
  const { id } = await params
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user) redirect('/login')

  const { data: project } = await supabase
    .from('projects')
    .select('*')
    .eq('id', id)
    .eq('user_id', user.id)
    .single()

  if (!project) redirect('/dashboard')

  const { data: clips } = await supabase
    .from('clips')
    .select('*')
    .eq('project_id', id)
    .order('virality_score', { ascending: false })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{project.title}</h1>
        <p className="text-sm text-muted-foreground capitalize">Status: {project.status}</p>
      </div>

      <WsProvider projectId={id}>
        <ProjectProgress />
        <ClipsGrid initialClips={(clips ?? []) as Clip[]} projectId={id} />
      </WsProvider>
    </div>
  )
}
