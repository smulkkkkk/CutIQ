export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background to-muted p-4">
      <div className="w-full max-w-sm space-y-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-xl bg-primary">
            <span className="text-2xl font-black text-primary-foreground">C</span>
          </div>
          <h1 className="text-2xl font-bold">CutIQ</h1>
          <p className="text-sm text-muted-foreground">Cortes virais com IA</p>
        </div>
        <div className="rounded-xl border bg-card p-6 shadow-sm">{children}</div>
      </div>
    </div>
  )
}
