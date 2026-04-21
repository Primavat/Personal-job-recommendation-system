'use client';
import React from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore, useThemeStore } from '@/lib/store';
import toast from 'react-hot-toast';

export default function Navbar() {
  const router = useRouter();
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const { theme } = useThemeStore();
  const isDark = theme === 'dark';

  const handleLogout = () => {
    clearAuth();
    toast.success('Logged out');
    router.push('/login');
  };

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/jobs', label: 'Browse Jobs' },
    { href: '/applications', label: 'Applications' },
    { href: '/analytics', label: 'Analytics' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 dark:bg-gray-900 dark:border-gray-700">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-black dark:bg-white rounded-lg flex items-center justify-center">
              <span className="text-white dark:text-black font-bold text-sm">J</span>
            </div>
            <span className="text-lg font-semibold text-gray-900 dark:text-white tracking-tight">JobRec</span>
          </Link>

          {/* Nav Links */}
          <div className="flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                  pathname === link.href
                    ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* User Menu */}
          {user && (
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-500 dark:text-gray-400">{user.email}</span>
              <Link
                href="/settings"
                className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                  pathname === '/settings'
                    ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}
              >
                Settings
              </Link>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-gray-900 dark:bg-white text-white dark:text-black text-sm font-medium rounded-lg hover:bg-gray-700 dark:hover:bg-gray-200 transition"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}