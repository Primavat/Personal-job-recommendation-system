export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Sign In</h2>

        <div className="space-y-4">
          <button className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium">
            Sign in with Supabase
          </button>

          <p className="text-center text-gray-600 text-sm">
            This feature will be connected to Supabase Auth
          </p>
        </div>

        <p className="text-center text-gray-500 text-xs mt-6">
          Protected by industry-standard security
        </p>
      </div>
    </div>
  );
}
