'use client';

import React, { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import { authAPI } from '@/lib/api';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user, setAuth, token } = useAuthStore();
  const [name, setName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [saving, setSaving] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeUploaded, setResumeUploaded] = useState(false);

  const handleSaveProfile = async () => {
    setSaving(true);
    try {
      const res = await authAPI.updateProfile({ name, email });
      setAuth(token!, { ...user!, name: res.data.name, email: res.data.email });
      toast.success('Profile updated');
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.type !== 'application/pdf') return toast.error('PDF only');
    if (file.size > 5 * 1024 * 1024) return toast.error('Max 5MB');
    setResumeFile(file);
  };

  const handleResumeUpload = () => {
    if (!resumeFile) return;
    toast.success(`Resume "${resumeFile.name}" saved`);
    setResumeUploaded(true);
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <div className="mb-10">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account and preferences</p>
      </div>

      <div className="space-y-6">

        {/* Profile */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
                placeholder="Your name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-gray-900 focus:border-transparent outline-none"
                placeholder="you@example.com"
              />
            </div>
            <button
              onClick={handleSaveProfile}
              disabled={saving}
              className="px-6 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition disabled:bg-gray-300"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>

        {/* Resume */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-1">Resume</h2>
          <p className="text-sm text-gray-500 mb-4">PDF only, max 5MB.</p>
          <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center hover:border-gray-300 transition">
            <input type="file" accept=".pdf" onChange={handleResumeChange} className="hidden" id="resume-upload" />
            <label htmlFor="resume-upload" className="cursor-pointer">
              <p className="text-sm font-medium text-gray-700">
                {resumeFile ? resumeFile.name : 'Click to upload your resume'}
              </p>
              <p className="text-xs text-gray-400 mt-1">PDF up to 5MB</p>
            </label>
          </div>
          {resumeFile && !resumeUploaded && (
            <button
              onClick={handleResumeUpload}
              className="mt-4 w-full px-4 py-2.5 bg-gray-900 text-white text-sm font-medium rounded-lg hover:bg-gray-700 transition"
            >
              Save Resume
            </button>
          )}
          {resumeUploaded && (
            <div className="mt-4 px-4 py-2.5 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 text-center">
              ✓ Resume uploaded successfully
            </div>
          )}
        </div>

      </div>
    </div>
  );
}