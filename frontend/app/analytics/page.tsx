'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { statsAPI } from '@/lib/api';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function AnalyticsPage() {
  const { data: analytics, error } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => statsAPI.getAnalytics(),
  });

  // Demo mode: mock analytics when backend is unavailable
  const isDemoMode = error && (error as any).isDemoModeError;
  const mockAnalytics = {
    overview: {
      total_jobs: 247,
      total_applications: 12,
      saved_count: 5,
      applied_count: 7,
    },
    by_category: [
      { category: 'Software Engineering', count: 85 },
      { category: 'AI / ML', count: 45 },
      { category: 'Frontend / Web', count: 38 },
      { category: 'Backend / Full Stack', count: 42 },
      { category: 'DevOps / Cloud', count: 25 },
      { category: 'Data Engineering', count: 12 },
    ],
    by_source: [
      { source: 'Remotive', count: 95 },
      { source: 'Arbeitnow', count: 78 },
      { source: 'The Muse', count: 52 },
      { source: 'FindWork', count: 22 },
    ],
  };

  const analyticsData = isDemoMode ? mockAnalytics : analytics?.data;

  if (!analyticsData) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-8">
        <p>Loading analytics...</p>
      </div>
    );
  }

  const categoryData = analyticsData.by_category || [];
  const sourceData = analyticsData.by_source || [];
  const overview = analyticsData.overview || {};

  const COLORS = [
    '#3b82f6',
    '#8b5cf6',
    '#ec4899',
    '#f59e0b',
    '#10b981',
    '#06b6d4',
    '#6366f1',
    '#f97316',
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics</h1>
            <p className="text-gray-600">
              Insights about the job market and your progress
            </p>
          </div>
          {!process.env.NEXT_PUBLIC_API_URL && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              ⚠️ Demo Mode
            </span>
          )}
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Jobs" value={overview.total_jobs} icon="📊" />
        <StatCard label="Saved" value={overview.saved_count} icon="💾" />
        <StatCard label="Applied" value={overview.applied_count} icon="📧" />
        <StatCard
          label="Total Applications"
          value={overview.total_applications}
          icon="📋"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Jobs by Category */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Jobs by Category
          </h2>
          {categoryData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-600">No data available</p>
          )}
        </div>

        {/* Jobs by Source */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-bold text-gray-900 mb-4">
            Jobs by Source
          </h2>
          {sourceData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={sourceData}
                  dataKey="count"
                  nameKey="source"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {sourceData.map((entry: any, index: number) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-600">No data available</p>
          )}
        </div>
      </div>

      {/* Table View */}
      <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Category Table */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Category Distribution
          </h3>
          <div className="space-y-2">
            {categoryData.map((item: any) => (
              <div key={item.category} className="flex justify-between items-center">
                <span className="text-gray-700">{item.category}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${(item.count / Math.max(...categoryData.map((c: any) => c.count))) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-gray-900 font-medium w-12 text-right">
                    {item.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Source Table */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">
            Source Distribution
          </h3>
          <div className="space-y-2">
            {sourceData.map((item: any) => (
              <div key={item.source} className="flex justify-between items-center">
                <span className="text-gray-700">{item.source}</span>
                <div className="flex items-center gap-2">
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{
                        width: `${(item.count / Math.max(...sourceData.map((s: any) => s.count))) * 100}%`,
                      }}
                    />
                  </div>
                  <span className="text-gray-900 font-medium w-12 text-right">
                    {item.count}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
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
      <p className="text-3xl font-bold text-gray-900">{(value || 0).toLocaleString()}</p>
    </div>
  );
}
