import { Check } from 'lucide-react'

interface PricingCardProps {
  name: string
  price: string
  period?: string
  description: string
  features: string[]
  highlighted?: boolean
  badge?: string
}

export function PricingCard({
  name, price, period, description, features, highlighted, badge,
}: PricingCardProps) {
  return (
    <div className={`relative rounded-2xl border p-6 space-y-5 flex flex-col ${
      highlighted
        ? 'border-primary bg-primary/5 shadow-lg shadow-primary/10'
        : 'bg-card'
    }`}>
      {badge && (
        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-primary px-3 py-1 text-xs font-semibold text-primary-foreground">
          {badge}
        </span>
      )}

      <div>
        <h3 className="text-lg font-bold">{name}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{description}</p>
      </div>

      <div className="flex items-end gap-1">
        <span className="text-4xl font-extrabold tracking-tight">{price}</span>
        {period && <span className="mb-1 text-sm text-muted-foreground">{period}</span>}
      </div>

      <ul className="space-y-2.5 flex-1">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-2 text-sm">
            <Check className="mt-0.5 size-4 shrink-0 text-green-500" />
            {feature}
          </li>
        ))}
      </ul>

      <button
        disabled
        className={`w-full rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
          highlighted
            ? 'bg-primary text-primary-foreground hover:bg-primary/90 cursor-not-allowed opacity-60'
            : 'border border-input bg-background hover:bg-accent cursor-not-allowed opacity-60'
        }`}
      >
        Em breve
      </button>
    </div>
  )
}
