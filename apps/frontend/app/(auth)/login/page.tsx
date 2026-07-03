import type { Metadata } from 'next'
import { LoginForm } from '@/components/forms/LoginForm'

export const metadata: Metadata = { title: 'Entrar — CutIQ' }

export default function LoginPage() {
  return (
    <>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Bem-vindo de volta</h2>
        <p className="text-sm text-muted-foreground">Entre na sua conta</p>
      </div>
      <LoginForm />
    </>
  )
}
