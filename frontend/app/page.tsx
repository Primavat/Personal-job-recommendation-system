import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-6">
      {/* Logo */}
      <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center mb-8">
        <span className="text-gray-950 text-2xl font-bold">J</span>
      </div>

      {/* Heading */}
      <h1 className="text-5xl font-bold text-white tracking-tight mb-4 text-center">
        JobRec
      </h1>
      <p className="text-gray-400 text-lg text-center max-w-md mb-12 leading-relaxed">
        AI-powered tech job recommendations, filtered and ranked just for you.
      </p>

      {/* CTA */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Link
          href="/login"
          className="px-8 py-3 bg-white text-gray-900 text-sm font-semibold rounded-xl hover:bg-gray-100 transition-all duration-200"
        >
          Get Started
        </Link>
        <Link
          href="/login"
          className="px-8 py-3 bg-transparent border border-gray-700 text-gray-300 text-sm font-semibold rounded-xl hover:border-gray-500 hover:text-white transition-all duration-200"
        >
          Sign In
        </Link>
      </div>

      {/* Subtle bottom text */}
      <p className="text-gray-600 text-xs mt-16 text-center">
        © {new Date().getFullYear()} JobRec · Built by Primavat
      </p>
    </div>
  );
}