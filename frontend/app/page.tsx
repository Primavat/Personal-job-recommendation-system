export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 bg-white rounded-lg flex items-center justify-center mx-auto mb-6">
          <span className="text-4xl font-bold text-blue-600">J</span>
        </div>
        <h1 className="text-4xl font-bold text-white mb-4">JobRec</h1>
        <p className="text-xl text-blue-100 mb-8">
          AI-Powered Tech Job Recommendations
        </p>
        <a
          href="/login"
          className="inline-block px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition"
        >
          Get Started
        </a>
      </div>
    </div>
  );
}
