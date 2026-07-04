'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api/client'
import { Upload, Link } from 'lucide-react'
import { cn } from '@/lib/utils'

type Mode = 'file' | 'youtube'

export function UploadForm() {
  const router = useRouter()
  const [mode, setMode] = useState<Mode>('file')
  const [title, setTitle] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      toast.error('Informe um título para o projeto')
      return
    }
    if (mode === 'file' && !file) {
      toast.error('Selecione um arquivo de vídeo')
      return
    }
    if (mode === 'youtube' && !youtubeUrl.trim()) {
      toast.error('Informe a URL do YouTube')
      return
    }

    setUploading(true)
    try {
      const project = await api.projects.create(title.trim())

      if (mode === 'file' && file) {
        const { id: video_id, upload_url } = await api.videos.create(
          project.id,
          file.name,
          file.type || 'video/mp4'
        )
        const xhr = new XMLHttpRequest()
        await new Promise<void>((resolve, reject) => {
          xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
              setUploadProgress(Math.round((e.loaded / e.total) * 100))
            }
          }
          xhr.onload = () => (xhr.status < 400 ? resolve() : reject(new Error(`Upload failed: ${xhr.status}`)))
          xhr.onerror = () => reject(new Error('Upload network error'))
          xhr.open('PUT', upload_url)
          xhr.setRequestHeader('Content-Type', file.type || 'video/mp4')
          xhr.send(file)
        })
        await api.videos.process(video_id)
      } else {
        await api.videos.importYoutube(project.id, youtubeUrl.trim())
      }

      toast.success('Processamento iniciado!')
      router.push(`/projects/${project.id}`)
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Erro ao enviar vídeo')
    } finally {
      setUploading(false)
      setUploadProgress(0)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-xl">
      <div className="space-y-2">
        <Label htmlFor="title">Nome do projeto</Label>
        <Input
          id="title"
          placeholder="Ex: Palestra sobre IA"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={uploading}
        />
      </div>

      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setMode('file')}
          className={cn(
            'flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
            mode === 'file'
              ? 'bg-primary text-primary-foreground border-primary'
              : 'border-input hover:bg-accent'
          )}
        >
          <Upload className="size-4" />
          Arquivo
        </button>
        <button
          type="button"
          onClick={() => setMode('youtube')}
          className={cn(
            'flex items-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium transition-colors',
            mode === 'youtube'
              ? 'bg-primary text-primary-foreground border-primary'
              : 'border-input hover:bg-accent'
          )}
        >
          <Link className="size-4" />
          YouTube
        </button>
      </div>

      {mode === 'file' ? (
        <div className="space-y-2">
          <Label htmlFor="file">Arquivo de vídeo</Label>
          <Input
            id="file"
            type="file"
            accept="video/*"
            disabled={uploading}
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>
      ) : (
        <div className="space-y-2">
          <Label htmlFor="youtube">URL do YouTube</Label>
          <Input
            id="youtube"
            placeholder="https://youtube.com/watch?v=..."
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            disabled={uploading}
          />
        </div>
      )}

      {uploading && mode === 'file' && uploadProgress > 0 && (
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Enviando... {uploadProgress}%</p>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-full bg-primary transition-all duration-300"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      <Button type="submit" disabled={uploading} className="w-full">
        {uploading ? 'Processando...' : 'Iniciar processamento'}
      </Button>
    </form>
  )
}
