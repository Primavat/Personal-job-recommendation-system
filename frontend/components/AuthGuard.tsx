'use client';
import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated());

  useEffect(() => {
    const publicRoutes = ['/login'];
    if (!isAuthenticated && !publicRoutes.includes(pathname)) {
      router.push('/login');
    }
  }, [isAuthenticated, pathname, router]);

  return <>{children}</>;
}