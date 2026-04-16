'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import toast from 'react-hot-toast';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [debugInfo, setDebugInfo] = useState('');
  const router = useRouter();
  const setAuth = useAuthStore((s) => s.setAuth);

  const handleLogin = async () => {
    if (!email) return toast.error('Please enter your email');
    setLoading(true);
    setDebugInfo('');
    try {
      const rawApiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const apiUrl = rawApiUrl.replace(/\/$/, '');
      setDebugInfo(`Connecting to: ${apiUrl}/api/auth/login`);

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
      router.push('/jobs');
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Login failed. Check your email.';
      setDebugInfo(`${errorMsg}`);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>
        <div className="space-y-4">
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleLogin}
            disabled={loading}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
          <p className="text-center text-gray-500 text-sm">
            Use: <span className="font-mono text-blue-600">test@example.com</span>
          </p>
          {debugInfo && (
            <div className="mt-4 p-3 bg-gray-100 rounded border border-gray-300">
              <p className="text-sm text-gray-700 font-mono break-words">{debugInfo}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}