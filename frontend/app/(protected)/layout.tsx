'use client';
import AuthGuard from '@/components/AuthGuard';
import Providers from '@/app/providers';
import Navbar from '@/components/Navbar';

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <Providers>
      <AuthGuard>
        <Navbar />
        <main className="min-h-screen bg-gray-50 dark:bg-gray-900">
          {children}
        </main>
      </AuthGuard>
    </Providers>
  );
}