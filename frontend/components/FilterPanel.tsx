'use client';

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { jobsAPI } from '@/lib/api';

interface FilterPanelProps {
  onFilterChange: (
    category?: string | null,
    location?: string | null,
    jobType?: string | null,
    source?: string | null
  ) => void;
}

export default function FilterPanel({ onFilterChange }: FilterPanelProps) {
  const [category, setCategory] = React.useState<string | null>(null);
  const [location, setLocation] = React.useState<string | null>(null);
  const [jobType, setJobType] = React.useState<string | null>(null);
  const [source, setSource] = React.useState<string | null>(null);

  const { data: categories } = useQuery({
    queryKey: ['categories'],
    queryFn: () => jobsAPI.getCategories(),
  });

  const { data: locations } = useQuery({
    queryKey: ['locations'],
    queryFn: () => jobsAPI.getLocations(),
  });

  const { data: sources } = useQuery({
    queryKey: ['sources'],
    queryFn: () => jobsAPI.getSources(),
  });

  const jobTypes = ['Internship', 'Full-time', 'Part-time', 'Contract', 'Freelance'];

  const handleChange = () => {
    onFilterChange(category, location, jobType, source);
  };

  React.useEffect(() => {
    handleChange();
  }, [category, location, jobType, source]);

  const handleReset = () => {
    setCategory(null);
    setLocation(null);
    setJobType(null);
    setSource(null);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>

      {/* Category */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Category
        </label>
        <select
          value={category || ''}
          onChange={(e) => setCategory(e.target.value || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Categories</option>
          {categories?.data?.map((cat: string) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>

      {/* Location */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Location
        </label>
        <select
          value={location || ''}
          onChange={(e) => setLocation(e.target.value || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Locations</option>
          {locations?.data?.slice(0, 20).map((loc: string) => (
            <option key={loc} value={loc}>
              {loc}
            </option>
          ))}
        </select>
      </div>

      {/* Job Type */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Job Type
        </label>
        <select
          value={jobType || ''}
          onChange={(e) => setJobType(e.target.value || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Types</option>
          {jobTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {/* Source */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Source
        </label>
        <select
          value={source || ''}
          onChange={(e) => setSource(e.target.value || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Sources</option>
          {sources?.data?.map((src: string) => (
            <option key={src} value={src}>
              {src}
            </option>
          ))}
        </select>
      </div>

      {/* Reset Button */}
      <button
        onClick={handleReset}
        className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-medium"
      >
        Reset Filters
      </button>
    </div>
  );
}
