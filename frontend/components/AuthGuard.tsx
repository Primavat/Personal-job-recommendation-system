'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/store'

export default function DashboardPage() {
  const router = useRouter()

  const token = useAuthStore((state) => state.token)
  const hasHydrated = useAuthStore((state) => state._hasHydrated)

  useEffect(() => {
    // 🚨 DO NOTHING until hydration completes
    if (!hasHydrated) return

    // ✅ Now safely check auth
    if (!token) {
      router.push('/')
    }
  }, [token, hasHydrated, router])

  // 🚨 Prevent UI flicker
  if (!hasHydrated) return null

  if (!token) return null

  return (
    <div>
      Dashboard
    </div>
  )
}