'use client'

import { motion } from 'framer-motion'
import { NavLinks } from '@/components/navigation/NavLinks'

export function Sidebar() {
  return (
    <motion.aside
      initial={{ x: -16, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.2 }}
      className="flex h-screen w-60 shrink-0 flex-col border-r bg-background px-4 py-6"
    >
      <div className="mb-8 flex items-center gap-2 px-3">
        <div className="flex size-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-black text-primary-foreground">C</span>
        </div>
        <span className="text-lg font-bold tracking-tight">CutIQ</span>
      </div>
      <NavLinks />
    </motion.aside>
  )
}
