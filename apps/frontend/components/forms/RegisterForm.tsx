'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase/client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'

export function RegisterForm() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password.length < 8) {
      toast.error('A senha deve ter ao menos 8 caracteres')
      return
    }
    setLoading(true)

    const supabase = createClient()
    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: { data: { full_name: name } },
    })

    if (error) {
      toast.error(error.message)
      setLoading(false)
      return
    }

    toast.success('Conta criada! Verifique seu email para confirmar.')
    router.push('/login')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Nome completo</Label>
        <Input
          id="name"
          type="text"
          placeholder="Seu Nome"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input
          id="email"
          type="email"
          placeholder="voce@exemplo.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="password">Senha</Label>
        <Input
          id="password"
          type="password"
          placeholder="Mín. 8 caracteres"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          autoComplete="new-password"
        />
      </div>
      <Button type="submit" className="w-full" disabled={loading}>
        {loading ? 'Criando conta...' : 'Criar conta grátis'}
      </Button>
      <p className="text-center text-sm text-muted-foreground">
        Já tem conta?{' '}
        <Link href="/login" className="text-primary underline-offset-4 hover:underline">
          Entrar
        </Link>
      </p>
    </form>
  )
}
