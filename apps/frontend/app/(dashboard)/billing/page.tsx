import { PricingCard } from '@/components/billing/PricingCard'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Planos — CutIQ',
}

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    description: 'Para experimentar',
    features: [
      '3 créditos por mês',
      'Resolução 720p',
      'Marca d\'água nos clips',
      'Máx. 30 min por vídeo',
      'Até 3 clips por projeto',
    ],
  },
  {
    name: 'Starter',
    price: '$19',
    period: '/mês',
    description: 'Para criadores em crescimento',
    features: [
      '25 créditos por mês',
      'Resolução 1080p',
      'Sem marca d\'água',
      'Máx. 2 horas por vídeo',
      'Até 10 clips por projeto',
      'Fila prioritária',
    ],
    highlighted: true,
    badge: 'Popular',
  },
  {
    name: 'Pro',
    price: '$49',
    period: '/mês',
    description: 'Para times e profissionais',
    features: [
      'Créditos ilimitados',
      'Resolução 1080p / 4K',
      'Sem marca d\'água',
      'Máx. 4 horas por vídeo',
      'Clips ilimitados por projeto',
      'Fila de alta prioridade',
    ],
  },
]

export default function BillingPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Planos</h1>
        <p className="text-muted-foreground">
          Escolha o plano ideal para sua criação de conteúdo
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-3 max-w-4xl">
        {PLANS.map(plan => (
          <PricingCard key={plan.name} {...plan} />
        ))}
      </div>

      <p className="text-xs text-muted-foreground">
        Pagamentos via Stripe — em breve disponível. Anual com 20% de desconto.
      </p>
    </div>
  )
}
