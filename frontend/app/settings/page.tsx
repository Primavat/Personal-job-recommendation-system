'use client';
export default function SettingsPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
            <p className="text-gray-600">
              Configure your preferences and pipeline settings
            </p>
          </div>
          {!process.env.NEXT_PUBLIC_API_URL && (
            <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-medium">
              ⚠️ Demo Mode
            </span>
          )}
        </div>
      </div>
      <div className="max-w-2xl">
        <div className="bg-white rounded-lg border border-gray-200 p-8">
          <div className="text-center py-12">
            <p className="text-gray-600 text-lg">⚙️ Settings page coming soon!</p>
            <p className="text-gray-500 mt-2">
              Here you'll be able to configure:
            </p>
            <ul className="text-gray-600 mt-4 space-y-2">
              <li>✓ Pipeline scheduling</li>
              <li>✓ Job preferences and filters</li>
              <li>✓ Notification settings</li>
              <li>✓ Account preferences</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}