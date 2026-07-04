export type Plan = 'free' | 'starter' | 'pro'

export interface Profile {
  id: string
  full_name: string | null
  avatar_url: string | null
  plan: Plan
  credits_used: number
  credits_limit: number
  is_admin: boolean
  created_at: string
  updated_at: string
}

export interface Project {
  id: string
  user_id: string
  title: string
  status: 'created' | 'uploading' | 'transcribing' | 'analyzing' | 'rendering' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface Video {
  id: string
  project_id: string
  source_type: 'upload' | 'youtube'
  filename: string
  status: 'pending' | 'processing' | 'transcribed' | 'failed'
  source_url: string | null
  r2_key: string | null
  duration_seconds: number | null
  size_bytes: number | null
  created_at: string
}

export interface Job {
  id: string
  project_id: string
  type: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  error_message: string | null
  created_at: string
}

export interface Clip {
  id: string
  project_id: string
  video_id: string
  title: string | null
  start_time: number
  end_time: number
  duration: number
  virality_score: number | null
  virality_reasons: string[] | null
  status: 'pending' | 'rendering' | 'ready' | 'failed'
  r2_key: string | null
  thumbnail_r2_key: string | null
  resolution: '720p' | '1080p' | '4k'
  has_watermark: boolean
  caption_style: string
  created_at: string
  updated_at: string
}

export interface JobProgressEvent {
  stage:
    | 'transcribing'
    | 'transcribed'
    | 'analyzing'
    | 'analyzed'
    | 'rendering'
    | 'clip_ready'
    | 'completed'
    | 'failed'
  progress?: number
  duration?: number
  clips_count?: number
  clip_id?: string
  thumbnail_url?: string
  message?: string
}
