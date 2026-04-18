'use client';

import React, { useState } from 'react';
import FilterPanel from '@/components/FilterPanel';
import JobList from '@/components/JobList';
import JobModal from '@/components/JobModal';
import { useFilterStore } from '@/lib/store';

export default function JobsPage() {
  const [selectedJobId, setSelectedJobId] = useState<string | null>(null);
  const {
    searchQuery,
    selectedCategory,
    selectedLocation,
    selectedJobType,
    selectedSource,
    setSearchQuery,
  } = useFilterStore();

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Browse Jobs</h1>
            <p className="text-gray-600">
              Discover tech jobs from multiple sources, filtered with AI
            </p>
          </div>
          {!process.env.NEXT_PUBLIC_API_URL && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              ⚠️ Demo Mode
            </span>
          )}
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-8">
        <input
          type="text"
          placeholder="Search jobs by title, company, or keywords..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Main Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Filters */}
        <div className="lg:col-span-1">
          <FilterPanel
            onFilterChange={(cat, loc, type, src) => {
              // Filters are handled by the FilterPanel component using Zustand
            }}
          />
        </div>

        {/* Job List */}
        <div className="lg:col-span-3">
          <JobList
            searchQuery={searchQuery}
            category={selectedCategory}
            location={selectedLocation}
            jobType={selectedJobType}
            source={selectedSource}
            onJobSelect={setSelectedJobId}
          />
        </div>
      </div>

      {/* Job Modal */}
      {selectedJobId && (
        <JobModal jobId={selectedJobId} onClose={() => setSelectedJobId(null)} />
      )}
    </div>
  );
}
