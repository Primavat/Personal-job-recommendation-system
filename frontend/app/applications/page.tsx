'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { applicationsAPI } from '@/lib/api';
import { getStatusColor } from '@/lib/utils';

export default function ApplicationsPage() {
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [page, setPage] = useState(1);

  const { data } = useQuery({
    queryKey: ['applications', filterStatus, page],
    queryFn: () =>
      applicationsAPI.list({
        status: filterStatus || undefined,
        page,
        limit: 20,
      }),
  });

  const applications = data?.data?.items || [];
  const total = data?.data?.total || 0;
  const pages = data?.data?.pages || 1;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Application Tracker</h1>
        <p className="text-gray-600">
          Track all your saved and applied jobs in one place
        </p>
      </div>

      {/* Status Filter */}
      <div className="mb-8 flex flex-wrap gap-2">
        {['saved', 'applied', 'rejected', 'interviewed', 'offered'].map(
          (status) => (
            <button
              key={status}
              onClick={() => {
                setFilterStatus(filterStatus === status ? null : status);
                setPage(1);
              }}
              className={`px-4 py-2 rounded-lg transition ${
                filterStatus === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </button>
          )
        )}
      </div>

      {/* Applications Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        {applications.length === 0 ? (
          <div className="p-8 text-center text-gray-600">
            No applications found. Start saving jobs to track them!
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Job Title
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Company
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Saved On
                    </th>
                    <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {applications.map((app: any) => (
                    <tr key={app.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-gray-900">
                          {app.job.title}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-gray-700">
                        {app.job.company}
                      </td>
                      <td className="px-6 py-4">
                        <span
                          className={`text-xs px-2 py-1 rounded-full ${getStatusColor(
                            app.status
                          )}`}
                        >
                          {app.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(app.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <a
                          href={app.job.apply_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                        >
                          View Job →
                        </a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex justify-center items-center space-x-4 px-6 py-4 border-t">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition"
              >
                Previous
              </button>
              <span className="text-gray-700">
                Page {page} of {pages}
              </span>
              <button
                onClick={() => setPage(Math.min(pages, page + 1))}
                disabled={page === pages}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg disabled:opacity-50 hover:bg-gray-300 transition"
              >
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
