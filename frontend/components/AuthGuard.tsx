'use client';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const token = useAuthStore((s) => s.token);
  const _hasHydrated = useAuthStore((s) => s._hasHydrated);

  useEffect(() => {
    if (!_hasHydrated) return; // wait for localStorage to load
    const publicRoutes = ['/login'];
    if (!token && !publicRoutes.includes(pathname)) {
      router.push('/login');
    }
  }, [_hasHydrated, token, pathname, router]);

  return <>{children}</>;
}