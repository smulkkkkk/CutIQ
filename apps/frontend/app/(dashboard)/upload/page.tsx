import type { Metadata } from 'next'
import { UploadForm } from '@/components/forms/UploadForm'

export const metadata: Metadata = {
  title: 'Novo Vídeo — CutIQ',
}

export default function UploadPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Novo vídeo</h1>
        <p className="text-muted-foreground">
          Faça upload de um arquivo ou importe diretamente do YouTube.
        </p>
      </div>
      <UploadForm />
    </div>
  )
}
