'use client';

import React from 'react';
import { getStatusColor, getJobTypeColor } from '@/lib/utils';

interface JobCardProps {
  id: string;
  title: string;
  company: string;
  location: string;
  jobType: string;
  category: string;
  datePosted: string;
  source: string;
  summary?: string;
  userStatus?: string;
  onClick?: () => void;
}

export default function JobCard({
  id,
  title,
  company,
  location,
  jobType,
  category,
  datePosted,
  source,
  summary,
  userStatus,
  onClick,
}: JobCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg transition cursor-pointer"
    >
      {/* Header */}
      <div className="mb-3">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2 hover:text-blue-600">
          {title}
        </h3>
        <p className="text-sm text-gray-600">{company}</p>
      </div>

      {/* Meta Info */}
      <div className="flex flex-wrap gap-2 mb-3">
        <span className={`text-xs px-2 py-1 rounded-full ${getJobTypeColor(jobType)}`}>
          {jobType}
        </span>
        <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
          {category}
        </span>
        <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800">
          {source}
        </span>
      </div>

      {/* Location & Date */}
      <div className="text-xs text-gray-600 space-y-1 mb-3">
        <p>📍 {location}</p>
        <p>📅 {datePosted}</p>
      </div>

      {/* Summary */}
      {summary && (
        <p className="text-sm text-gray-700 mb-3 line-clamp-2">{summary}</p>
      )}

      {/* Status Badge */}
      {userStatus && (
        <div className={`text-xs px-2 py-1 rounded-full ${getStatusColor(userStatus)} inline-block`}>
          {userStatus}
        </div>
      )}
    </div>
  );
}
