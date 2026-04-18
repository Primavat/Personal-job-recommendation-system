'use client';

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelineAPI, statsAPI } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const queryClient = useQueryClient();

  // ── Latest pipeline run — polls every 3 s while status is "running" ────────
  const { data: latestRun } = useQuery({
    queryKey: ['latest-run'],
    queryFn: () => pipelineAPI.getStatus(),
    refetchInterval: (query) => {
      const status = query.state.data?.data?.status;
      return status === 'running' ? 3000 : false;
    },
    refetchIntervalInBackground: false,
  });

  const isRunning = latestRun?.data?.status === 'running';

  // ── Stats — refreshed automatically when a run finishes ───────────────────
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsAPI.getOverview(),
  });

  // Detect pipeline run transitions and react accordingly
  const prevStatus = React.useRef<string | undefined>(undefined);
  React.useEffect(() => {
    const status = latestRun?.data?.status;
    if (prevStatus.current === 'running' && status !== 'running') {
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      if (status === 'completed') {
        toast.success(
          `Pipeline finished! ${latestRun?.data?.jobs_added ?? 0} jobs added.`
        );
      } else if (status === 'failed') {
        toast.error('Pipeline failed. Check the backend logs.');
      }
    }
    prevStatus.current = status;
  }, [latestRun?.data?.status, latestRun?.data?.jobs_added, queryClient]);

  // ── Trigger pipeline mutation ───────────────────────────────────────────────
  const pipelineMutation = useMutation({
    mutationFn: () => pipelineAPI.run(),
    onSuccess: () => {
      toast.success('Pipeline started! Collecting jobs in the background…');
      queryClient.invalidateQueries({ queryKey: ['latest-run'] });
    },
    onError: () => {
      toast.error('Failed to start pipeline. Please try again.');
    },
  });

  const statsData = stats?.data?.overview;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your job search overview.</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Jobs"   value={statsData?.total_jobs         || 0} icon="📊" />
        <StatCard label="Saved Jobs"   value={statsData?.saved_count        || 0} icon="💾" />
        <StatCard label="Applied"      value={statsData?.applied_count      || 0} icon="📧" />
        <StatCard label="Applications" value={statsData?.total_applications || 0} icon="📋" />
      </div>

      {/* Pipeline Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900">Pipeline Status</h2>

          {/* Live status badge */}
          {isRunning && (
            <span className="flex items-center gap-2 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-full px-3 py-1 animate-pulse">
              <span className="w-2 h-2 rounded-full bg-blue-600 inline-block" />
              Running…
            </span>
          )}
          {latestRun?.data?.status === 'completed' && (
            <span className="flex items-center gap-2 text-sm font-medium text-green-700 bg-green-50 border border-green-200 rounded-full px-3 py-1">
              ✅ Completed
            </span>
          )}
          {latestRun?.data?.status === 'failed' && (
            <span className="flex items-center gap-2 text-sm font-medium text-red-700 bg-red-50 border border-red-200 rounded-full px-3 py-1">
              ❌ Failed
            </span>
          )}
        </div>

        {latestRun?.data ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div>
              <p className="text-gray-500 text-sm">Last Started</p>
              <p className="text-base font-semibold text-gray-900">
                {formatDateTime(latestRun.data.started_at)}
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Jobs Collected</p>
              <p className="text-base font-semibold text-gray-900">
                {latestRun.data.jobs_collected ?? '—'}
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Jobs Processed</p>
              <p className="text-base font-semibold text-gray-900">
                {latestRun.data.jobs_processed ?? '—'}
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">Jobs Added</p>
              <p className="text-base font-semibold text-gray-900">
                {latestRun.data.jobs_added ?? '—'}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 mb-6">No pipeline runs yet. Start collecting jobs!</p>
        )}

        <button
          id="run-pipeline-btn"
          onClick={() => pipelineMutation.mutate()}
          disabled={isRunning || pipelineMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-gray-300 disabled:cursor-not-allowed font-medium"
        >
          {isRunning
            ? '🔄 Pipeline is running…'
            : pipelineMutation.isPending
            ? '⏳ Triggering…'
            : '🚀 Run Pipeline Now'}
        </button>

        {isRunning && (
          <p className="text-sm text-gray-500 mt-3">
            ⏱ This usually takes 1–3 minutes. This page updates automatically.
          </p>
        )}
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <a href="/jobs" className="bg-blue-50 border border-blue-200 rounded-lg p-6 hover:shadow-lg transition">
          <h3 className="font-bold text-gray-900 mb-2">🔍 Browse All Jobs</h3>
          <p className="text-gray-600">Search and filter through available jobs</p>
        </a>
        <a href="/applications" className="bg-purple-50 border border-purple-200 rounded-lg p-6 hover:shadow-lg transition">
          <h3 className="font-bold text-gray-900 mb-2">📋 My Applications</h3>
          <p className="text-gray-600">Track your saved and applied positions</p>
        </a>
        <a href="/analytics" className="bg-green-50 border border-green-200 rounded-lg p-6 hover:shadow-lg transition">
          <h3 className="font-bold text-gray-900 mb-2">📈 Analytics</h3>
          <p className="text-gray-600">View trends and insights about the job market</p>
        </a>
        <a href="/settings" className="bg-orange-50 border border-orange-200 rounded-lg p-6 hover:shadow-lg transition">
          <h3 className="font-bold text-gray-900 mb-2">⚙️ Settings</h3>
          <p className="text-gray-600">Configure pipeline and preferences</p>
        </a>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: number;
  icon: string;
}) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <p className="text-4xl mb-2">{icon}</p>
      <p className="text-gray-600 text-sm mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
    </div>
  );
}
