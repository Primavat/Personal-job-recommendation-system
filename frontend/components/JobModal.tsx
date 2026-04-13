'use client';

import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { jobsAPI, applicationsAPI } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import toast from 'react-hot-toast';

interface JobModalProps {
  jobId: string;
  onClose: () => void;
}

export default function JobModal({ jobId, onClose }: JobModalProps) {
  const [userNotes, setUserNotes] = useState('');

  const { data: job } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsAPI.get(jobId),
  });

  const { data: application } = useQuery({
    queryKey: ['application', jobId],
    queryFn: () => applicationsAPI.get(jobId),
  });

  const saveMutation = useMutation({
    mutationFn: () => applicationsAPI.save(jobId),
    onSuccess: () => {
      toast.success('Job saved!');
    },
    onError: () => {
      toast.error('Failed to save job');
    },
  });

  const updateMutation = useMutation({
    mutationFn: (status: string) =>
      applicationsAPI.update(jobId, { status, notes: userNotes }),
    onSuccess: () => {
      toast.success('Application updated!');
    },
    onError: () => {
      toast.error('Failed to update application');
    },
  });

  const jobData = job?.data;

  if (!jobData) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full mx-4 my-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{jobData.title}</h2>
            <p className="text-lg text-gray-600">{jobData.company}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ✕
          </button>
        </div>

        {/* Meta Info */}
        <div className="grid grid-cols-2 gap-4 mb-6 pb-6 border-b">
          <div>
            <p className="text-gray-600 text-sm">Location</p>
            <p className="text-gray-900 font-medium">{jobData.location}</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Job Type</p>
            <p className="text-gray-900 font-medium">{jobData.job_type}</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Category</p>
            <p className="text-gray-900 font-medium">{jobData.category}</p>
          </div>
          <div>
            <p className="text-gray-600 text-sm">Posted</p>
            <p className="text-gray-900 font-medium">{jobData.date_posted}</p>
          </div>
        </div>

        {/* Summary & Description */}
        <div className="mb-6">
          {jobData.ai_summary && (
            <>
              <h3 className="font-semibold text-gray-900 mb-2">AI Summary</h3>
              <p className="text-gray-700 mb-4">{jobData.ai_summary}</p>
            </>
          )}
          {jobData.description && (
            <>
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-gray-700 whitespace-pre-wrap mb-4">
                {jobData.description}
              </p>
            </>
          )}
        </div>

        {/* User Notes */}
        <div className="mb-6 pb-6 border-b">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Your Notes
          </label>
          <textarea
            value={userNotes || (application?.data?.notes || '')}
            onChange={(e) => setUserNotes(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            rows={3}
            placeholder="Add notes about this job..."
          />
        </div>

        {/* Actions */}
        <div className="flex justify-between gap-4">
          <a
            href={jobData.apply_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-center font-medium"
          >
            Apply Now →
          </a>

          {!application?.data ? (
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-medium disabled:opacity-50"
            >
              💾 Save Job
            </button>
          ) : (
            <div className="flex gap-2 flex-1">
              <select
                value={application.data.status}
                onChange={(e) => updateMutation.mutate(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="saved">Saved</option>
                <option value="applied">Applied</option>
                <option value="rejected">Rejected</option>
                <option value="interviewed">Interviewed</option>
                <option value="offered">Offered</option>
              </select>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
