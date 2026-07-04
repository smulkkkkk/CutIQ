import { createClient } from '@/lib/supabase/client'
import type { Profile, Project, Video } from '@/types'

async function getAuthHeader(): Promise<Record<string, string>> {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) return {}
  return { Authorization: `Bearer ${session.access_token}` }
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const authHeader = await getAuthHeader()
  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(error.detail ?? 'API error')
  }
  return res.json()
}

export const api = {
  auth: {
    me: () => apiFetch<Profile>('/api/auth/me'),
  },
  projects: {
    list: () => apiFetch<Project[]>('/api/projects'),
    create: (title: string) =>
      apiFetch<Project>('/api/projects', {
        method: 'POST',
        body: JSON.stringify({ title }),
      }),
    get: (id: string) => apiFetch<Project>(`/api/projects/${id}`),
  },
  videos: {
    create: (project_id: string, filename: string, content_type = 'video/mp4') =>
      apiFetch<{ video_id: string; upload_url: string }>('/api/videos', {
        method: 'POST',
        body: JSON.stringify({ project_id, filename, content_type }),
      }),
    process: (video_id: string) =>
      apiFetch<{ job_id: string }>(`/api/videos/${video_id}/process`, {
        method: 'POST',
      }),
    importYoutube: (project_id: string, url: string) =>
      apiFetch<{ video_id: string; job_id: string }>('/api/videos/import-youtube', {
        method: 'POST',
        body: JSON.stringify({ project_id, url }),
      }),
  },
}
