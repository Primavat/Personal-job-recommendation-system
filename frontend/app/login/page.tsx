'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState('');

  const handleLogin = async () => {
    if (!email) return toast.error('Please enter your email');
    setLoading(true);
    setDebugInfo('');
    try {
      const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const apiUrl = rawApiUrl.replace(/\/$/, '');

      // Demo mode: if no API URL is set, use demo login
      if (!process.env.NEXT_PUBLIC_API_URL) {
        console.log('Demo mode: using mock login');
        const mockUser = { id: 'demo-user-id', email };
        const mockToken = 'demo-token-' + Date.now();
        setAuth(mockToken, mockUser);
        toast.success('Logged in (Demo Mode)');
        await new Promise((resolve) => setTimeout(resolve, 100));
        router.push('/dashboard');
        return;
      }

      const res = await fetch(`${apiUrl}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      if (!res.ok) {
        setDebugInfo(`Error: ${res.status} - ${data.detail || 'Unknown error'}`);
        throw new Error(data.detail || 'Login failed');
      }

      setAuth(data.token, data.user);
      toast.success('Logged in!');

      // Wait one tick for Zustand persist to write to localStorage
      //    before navigating — prevents the race condition
      await new Promise((resolve) => setTimeout(resolve, 100));
      router.push('/dashboard');

    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed. Check your email.';
      setDebugInfo(`${errorMsg}`);
      
      // If backend is not available, fallback to demo mode
      if (errorMsg.includes('fetch') || errorMsg.includes('ECONNREFUSED') || errorMsg.includes('Network')) {
        console.log('Backend not available, falling back to demo mode');
        const mockUser = { id: 'demo-user-id', email };
        const mockToken = 'demo-token-' + Date.now();
        setAuth(mockToken, mockUser);
        toast.success('Logged in (Demo Mode - Backend unavailable)');
        await new Promise((resolve) => setTimeout(resolve, 100));
        router.push('/dashboard');
        return;
      }
      
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-3xl font-bold">J</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">JobRec</h1>
          <p className="text-gray-600">AI-Powered Job Recommendations</p>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleLogin()}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Enter your email"
              disabled={loading}
            />
          </div>

          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Logging in...' : 'Login'}
          </button>

          {debugInfo && (
            <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
              {debugInfo}
            </div>
          )}

          <p className="text-center text-sm text-gray-500">
            For demo, use any email address
          </p>
        </div>
      </div>
    </div>
  );
}