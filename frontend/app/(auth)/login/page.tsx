'use client';
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store';
import { authAPI } from '@/lib/api';
import toast from 'react-hot-toast';
import ThemeToggle from '@/components/ThemeToggle';

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email || !password) return toast.error('Please fill in all fields');
    if (isRegister && !name) return toast.error('Please enter your name');
    setLoading(true);
    try {
      const res = isRegister
        ? await authAPI.register(email, password, name)
        : await authAPI.login(email, password);

      setAuth(res.data.token, res.data.user);
      toast.success(isRegister ? 'Account created!' : 'Welcome back!');
      await new Promise((r) => setTimeout(r, 100));
      router.push('/dashboard');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      {/* Theme Toggle */}
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="w-12 h-12 bg-black rounded-xl flex items-center justify-center mx-auto mb-4">
            <span className="text-white text-xl font-bold">J</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">JobRec</h1>
          <p className="text-gray-500 text-sm mt-1">AI-Powered Job Recommendations</p>
        </div>

        <div className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
                placeholder="Your name"
                disabled={loading}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
              placeholder="you@example.com"
              disabled={loading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
              placeholder="••••••••"
              disabled={loading}
            />
          </div>

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full px-4 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
          >
            {loading ? 'Please wait...' : isRegister ? 'Create Account' : 'Login'}
          </button>

          <p className="text-center text-sm text-gray-500">
            {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
            <button
              onClick={() => setIsRegister(!isRegister)}
              className="text-gray-900 font-medium hover:underline"
            >
              {isRegister ? 'Login' : 'Register'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}