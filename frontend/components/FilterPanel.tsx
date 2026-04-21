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
  onReset?: () => void;
}

export default function FilterPanel({ onFilterChange, onReset }: FilterPanelProps) {
  const [category, setCategory] = React.useState<string | null>(null);
  const [location, setLocation] = React.useState<string | null>(null);
  const [jobType, setJobType] = React.useState<string | null>(null);
  const [source, setSource] = React.useState<string | null>(null);

  const [appliedCategory, setAppliedCategory] = React.useState<string | null>(null);
  const [appliedLocation, setAppliedLocation] = React.useState<string | null>(null);
  const [appliedJobType, setAppliedJobType] = React.useState<string | null>(null);
  const [appliedSource, setAppliedSource] = React.useState<string | null>(null);

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

  // Dynamically filter India locations from API data
  const indiaLocations = locations?.data?.filter((loc: string) =>
    loc && (
      loc.toLowerCase().includes('india') ||
      loc.toLowerCase().includes('gujarat') ||
      loc.toLowerCase().includes('karnataka') ||
      loc.toLowerCase().includes('tamil nadu') ||
      loc.toLowerCase().includes('maharashtra') ||
      loc.toLowerCase().includes('telangana') ||
      loc.toLowerCase().includes('uttar pradesh') ||
      loc.toLowerCase().includes('rajasthan') ||
      loc.toLowerCase().includes('west bengal') ||
      loc.toLowerCase().includes('bangalore') ||
      loc.toLowerCase().includes('mumbai') ||
      loc.toLowerCase().includes('delhi') ||
      loc.toLowerCase().includes('hyderabad') ||
      loc.toLowerCase().includes('pune') ||
      loc.toLowerCase().includes('chennai') ||
      loc.toLowerCase().includes('kolkata') ||
      loc.toLowerCase().includes('ahmedabad') ||
      loc.toLowerCase().includes('noida') ||
      loc.toLowerCase().includes('gurgaon') ||
      loc.toLowerCase().includes('coimbatore') ||
      loc.toLowerCase().includes('remote (india)')
    )
  ) ?? [];

  // Dynamically filter global/remote locations
  const globalLocations = locations?.data?.filter((loc: string) =>
    loc && (
      loc.toLowerCase() === 'remote' ||
      loc.toLowerCase().includes('remote (global)') ||
      loc.toLowerCase().includes('worldwide') ||
      loc.toLowerCase().includes('anywhere')
    )
  ) ?? [];

  // Everything else
  const indiaSet = new Set(indiaLocations);
  const globalSet = new Set(globalLocations);
  const otherLocations = locations?.data?.filter(
    (loc: string) => loc && !indiaSet.has(loc) && !globalSet.has(loc)
  ) ?? [];

  const hasPendingChanges =
    category !== appliedCategory ||
    location !== appliedLocation ||
    jobType !== appliedJobType ||
    source !== appliedSource;

  const hasActiveFilters =
    appliedCategory || appliedLocation || appliedJobType || appliedSource;

  const handleApply = () => {
    setAppliedCategory(category);
    setAppliedLocation(location);
    setAppliedJobType(jobType);
    setAppliedSource(source);
    onFilterChange(category, location, jobType, source);
  };

  const handleReset = () => {
    setCategory(null);
    setLocation(null);
    setJobType(null);
    setSource(null);
    setAppliedCategory(null);
    setAppliedLocation(null);
    setAppliedJobType(null);
    setAppliedSource(null);
    onFilterChange(null, null, null, null);
    onReset?.();
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-black">Filters</h3>
        {hasActiveFilters && (
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
            Active
          </span>
        )}
      </div>

      {/* Category */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-black mb-2">
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
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-black mb-2">
          Location
        </label>
        <select
          value={location || ''}
          onChange={(e) => setLocation(e.target.value || null)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">All Locations</option>
          {indiaLocations.length > 0 && (
            <optgroup label="🇮🇳 India">
              {indiaLocations.map((loc: string) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </optgroup>
          )}
          {globalLocations.length > 0 && (
            <optgroup label="🌍 Global / Remote">
              {globalLocations.map((loc: string) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </optgroup>
          )}
          {otherLocations.length > 0 && (
            <optgroup label="Other">
              {otherLocations.slice(0, 30).map((loc: string) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </optgroup>
          )}
        </select>
      </div>

      {/* Job Type */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 dark:text-black mb-2">
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
        <label className="block text-sm font-medium text-gray-700 dark:text-black mb-2">
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

      {/* Apply Button */}
      <button
        onClick={handleApply}
        disabled={!hasPendingChanges}
        className={`w-full px-4 py-2 rounded-lg font-medium transition mb-2 ${
          hasPendingChanges
            ? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
            : 'bg-blue-100 text-blue-300 cursor-not-allowed'
        }`}
      >
        Apply Filters
      </button>

      {/* Reset Button */}
      <button
        onClick={handleReset}
        disabled={!hasActiveFilters && !hasPendingChanges}
        className={`w-full px-4 py-2 rounded-lg font-medium transition ${
          hasActiveFilters || hasPendingChanges
            ? 'bg-gray-200 text-gray-800 hover:bg-gray-300 cursor-pointer'
            : 'bg-gray-100 text-gray-400 cursor-not-allowed'
        }`}
      >
        Reset Filters
      </button>
    </div>
  );
}