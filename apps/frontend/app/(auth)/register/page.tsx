import type { Metadata } from 'next'
import { RegisterForm } from '@/components/forms/RegisterForm'

export const metadata: Metadata = { title: 'Criar conta — CutIQ' }

export default function RegisterPage() {
  return (
    <>
      <div className="mb-6">
        <h2 className="text-xl font-semibold">Criar conta grátis</h2>
        <p className="text-sm text-muted-foreground">3 projetos gratuitos por mês</p>
      </div>
      <RegisterForm />
    </>
  )
}
