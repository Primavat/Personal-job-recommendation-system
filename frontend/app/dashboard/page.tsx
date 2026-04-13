'use client';

import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { pipelineAPI, statsAPI } from '@/lib/api';
import { formatDateTime } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const queryClient = useQueryClient();
  const [isRunning, setIsRunning] = React.useState(false);

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => statsAPI.getOverview(),
  });

  const { data: latestRun } = useQuery({
    queryKey: ['latest-run'],
    queryFn: () => pipelineAPI.getStatus(),
  });

  const pipelineMutation = useMutation({
    mutationFn: () => pipelineAPI.run(),
    onMutate: () => setIsRunning(true),
    onSuccess: () => {
      toast.success('Pipeline started! Jobs are being collected...');
      queryClient.invalidateQueries({ queryKey: ['latest-run'] });
      queryClient.invalidateQueries({ queryKey: ['stats'] });
      setIsRunning(false);
    },
    onError: () => {
      toast.error('Failed to start pipeline');
      setIsRunning(false);
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
        <StatCard
          label="Total Jobs"
          value={statsData?.total_jobs || 0}
          icon="📊"
        />
        <StatCard
          label="Saved Jobs"
          value={statsData?.saved_count || 0}
          icon="💾"
        />
        <StatCard
          label="Applied"
          value={statsData?.applied_count || 0}
          icon="📧"
        />
        <StatCard
          label="Applications"
          value={statsData?.total_applications || 0}
          icon="📋"
        />
      </div>

      {/* Pipeline Section */}
      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Pipeline Status</h2>

        {latestRun?.data ? (
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <p className="text-gray-600 text-sm">Status</p>
              <p className="text-lg font-semibold text-gray-900">
                {latestRun.data.status === 'completed' ? '✅' : '🔄'} {latestRun.data.status}
              </p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Last Run</p>
              <p className="text-lg font-semibold text-gray-900">
                {formatDateTime(latestRun.data.started_at)}
              </p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Jobs Collected</p>
              <p className="text-lg font-semibold text-gray-900">
                {latestRun.data.jobs_collected}
              </p>
            </div>
            <div>
              <p className="text-gray-600 text-sm">Jobs Added</p>
              <p className="text-lg font-semibold text-gray-900">
                {latestRun.data.jobs_added}
              </p>
            </div>
          </div>
        ) : (
          <p className="text-gray-600 mb-6">No pipeline runs yet. Start collecting jobs!</p>
        )}

        <button
          onClick={() => pipelineMutation.mutate()}
          disabled={isRunning || pipelineMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 font-medium"
        >
          {isRunning ? '🔄 Running...' : '🚀 Run Pipeline Now'}
        </button>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <a
          href="/jobs"
          className="bg-blue-50 border border-blue-200 rounded-lg p-6 hover:shadow-lg transition"
        >
          <h3 className="font-bold text-gray-900 mb-2">🔍 Browse All Jobs</h3>
          <p className="text-gray-600">Search and filter through available jobs</p>
        </a>
        <a
          href="/applications"
          className="bg-purple-50 border border-purple-200 rounded-lg p-6 hover:shadow-lg transition"
        >
          <h3 className="font-bold text-gray-900 mb-2">📋 My Applications</h3>
          <p className="text-gray-600">Track your saved and applied positions</p>
        </a>
        <a
          href="/analytics"
          className="bg-green-50 border border-green-200 rounded-lg p-6 hover:shadow-lg transition"
        >
          <h3 className="font-bold text-gray-900 mb-2">📈 Analytics</h3>
          <p className="text-gray-600">View trends and insights about job market</p>
        </a>
        <a
          href="/settings"
          className="bg-orange-50 border border-orange-200 rounded-lg p-6 hover:shadow-lg transition"
        >
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
