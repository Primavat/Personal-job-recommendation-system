/**
 * Utility functions for the frontend
 */

export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function formatDateTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function truncateText(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    saved: 'bg-blue-100 text-blue-800',
    applied: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    interviewed: 'bg-purple-100 text-purple-800',
    offered: 'bg-yellow-100 text-yellow-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}

export function getJobTypeColor(type: string): string {
  const colors: Record<string, string> = {
    internship: 'bg-cyan-100 text-cyan-800',
    'full-time': 'bg-green-100 text-green-800',
    'part-time': 'bg-orange-100 text-orange-800',
    contract: 'bg-red-100 text-red-800',
    freelance: 'bg-purple-100 text-purple-800',
  };
  return colors[type.toLowerCase()] || 'bg-gray-100 text-gray-800';
}
