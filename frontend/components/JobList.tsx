'use client';

import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { jobsAPI } from '@/lib/api';
import JobCard from './JobCard';

interface JobListProps {
  searchQuery?: string;
  category?: string | null;
  location?: string | null;
  jobType?: string | null;
  source?: string | null;
  onJobSelect?: (jobId: string) => void;
}

export default function JobList({
  searchQuery = '',
  category,
  location,
  jobType,
  source,
  onJobSelect,
}: JobListProps) {
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data, isLoading, error } = useQuery({
    queryKey: [
      'jobs',
      page,
      searchQuery,
      category,
      location,
      jobType,
      source,
    ],
    queryFn: () =>
      jobsAPI.list({
        page,
        limit,
        search: searchQuery || undefined,
        category: category || undefined,
        location: location || undefined,
        job_type: jobType || undefined,
        source: source || undefined,
      }),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Demo mode: mock jobs when backend is unavailable
  const isDemoMode = error && (error as any).isDemoModeError;
  const mockJobs = [
    {
      id: '1',
      title: 'Software Engineering Intern',
      company: 'Google',
      location: 'Bangalore, India',
      job_type: 'Internship',
      category: 'Software Engineering',
      date_posted: '2024-01-15',
      source: 'Demo',
      ai_summary: 'Looking for passionate CS students to join our team.',
      user_application_status: null,
    },
    {
      id: '2',
      title: 'ML Engineer',
      company: 'OpenAI',
      location: 'Remote',
      job_type: 'Full-time',
      category: 'AI / ML',
      date_posted: '2024-01-14',
      source: 'Demo',
      ai_summary: 'Build cutting-edge AI systems.',
      user_application_status: null,
    },
    {
      id: '3',
      title: 'Frontend Developer',
      company: 'Meta',
      location: 'San Francisco, USA',
      job_type: 'Full-time',
      category: 'Frontend / Web',
      date_posted: '2024-01-13',
      source: 'Demo',
      ai_summary: 'Work on React and modern web technologies.',
      user_application_status: null,
    },
    {
      id: '4',
      title: 'DevOps Engineer',
      company: 'AWS',
      location: 'Remote',
      job_type: 'Full-time',
      category: 'DevOps / Cloud',
      date_posted: '2024-01-12',
      source: 'Demo',
      ai_summary: 'Manage cloud infrastructure at scale.',
      user_application_status: null,
    },
    {
      id: '5',
      title: 'Data Scientist',
      company: 'Microsoft',
      location: 'Seattle, USA',
      job_type: 'Full-time',
      category: 'Data Engineering',
      date_posted: '2024-01-11',
      source: 'Demo',
      ai_summary: 'Analyze data to drive business decisions.',
      user_application_status: null,
    },
  ];

  const jobs = isDemoMode ? mockJobs : (data?.data?.items || []);
  const total = isDemoMode ? mockJobs.length : (data?.data?.total || 0);
  const pages = isDemoMode ? 1 : (data?.data?.pages || 1);

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array(5).fill(null).map((_, i) => (
          <div key={i} className="h-40 bg-gray-200 rounded-lg animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Failed to load jobs</p>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">No jobs found. Try adjusting your filters.</p>
      </div>
    );
  }

  return (
    <div>
      {/* Jobs Grid */}
      <div className="grid grid-cols-1 gap-4 mb-8">
        {jobs.map((job: any) => (
          <JobCard
            key={job.id}
            id={job.id}
            title={job.title}
            company={job.company}
            location={job.location}
            jobType={job.job_type}
            category={job.category}
            datePosted={job.date_posted}
            source={job.source}
            summary={job.ai_summary}
            userStatus={job.user_application_status}
            onClick={() => onJobSelect?.(job.id)}
          />
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center space-x-4">
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

      {/* Stats */}
      <div className="mt-4 text-center text-sm text-gray-600">
        Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total} jobs
      </div>
    </div>
  );
}
