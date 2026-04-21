'use client';

import React, { useState } from 'react';
import { useAuthStore } from '@/lib/store';
import toast from 'react-hot-toast';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeUploaded, setResumeUploaded] = useState(false);

  const handleResumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.type !== 'application/pdf') {
      toast.error('Only PDF files are supported');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be under 5MB');
      return;
    }
    setResumeFile(file);
  };

  const handleResumeUpload = () => {
    if (!resumeFile) return;
    // Placeholder — wire to your backend when ready
    toast.success(`Resume "${resumeFile.name}" saved successfully`);
    setResumeUploaded(true);
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-500 mt-1">Manage your account and preferences</p>
      </div>

      <div className="space-y-6">

        {/* Profile Section */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-4">Profile</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Name
              </label>
              <div className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 text-sm">
                {user?.email?.split('@')[0] || '—'}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-600 mb-1">
                Email Address
              </label>
              <div className="px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 text-sm">
                {user?.email || '—'}
              </div>
            </div>
          </div>
        </div>

        {/* Resume Section */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-1">Resume</h2>
          <p className="text-sm text-gray-500 mb-4">
            Upload your resume to attach it to job applications. PDF only, max 5MB.
          </p>

          <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 text-center hover:border-gray-300 transition">
            <input
              type="file"
              accept=".pdf"
              onChange={handleResumeChange}
              className="hidden"
              id="resume-upload"
            />
            <label htmlFor="resume-upload" className="cursor-pointer">
              <div className="text-3xl mb-2">📄</div>
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

        {/* Preferences Section */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h2 className="text-base font-semibold text-gray-900 mb-1">Preferences</h2>
          <p className="text-sm text-gray-500 mb-4">More settings coming soon.</p>
          <div className="space-y-3 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-gray-100 flex items-center justify-center text-xs">✓</span>
              Pipeline scheduling
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-gray-100 flex items-center justify-center text-xs">✓</span>
              Notification settings
            </div>
            <div className="flex items-center gap-2">
              <span className="w-4 h-4 rounded-full bg-gray-100 flex items-center justify-center text-xs">✓</span>
              Job preferences
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}