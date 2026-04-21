import Link from 'next/link';
import ThemeToggle from '@/components/ThemeToggle';

export default function Home() {
  return (
    <div className="min-h-screen bg-gray-950 dark:bg-black flex flex-col items-center justify-center px-6">
      {/* Theme Toggle */}
      <div className="absolute top-6 right-6">
        <ThemeToggle />
      </div>

      {/* Logo */}
      <div className="w-14 h-14 bg-white dark:bg-white rounded-2xl flex items-center justify-center mb-8 border border-gray-700 dark:border-gray-600">
        <span className="text-gray-950 dark:text-gray-900 text-2xl font-bold">J</span>
      </div>

      {/* Heading */}
      <h1 className="text-5xl font-bold text-white dark:text-white tracking-tight mb-4 text-center">
        JobRec
      </h1>
      <p className="text-gray-400 dark:text-gray-300 text-lg text-center max-w-md mb-12 leading-relaxed">
        AI-powered tech job recommendations, filtered and ranked just for you.
      </p>

      {/* CTA */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Link
          href="/login"
          className="px-8 py-3 bg-white dark:bg-white text-gray-900 dark:text-gray-900 text-sm font-semibold rounded-xl hover:bg-gray-100 dark:hover:bg-gray-200 transition-all duration-200 border border-gray-900 dark:border-gray-600"
        >
          Get Started
        </Link>
        <Link
          href="/login"
          className="px-8 py-3 bg-transparent border border-gray-700 dark:border-gray-600 text-gray-300 dark:text-gray-300 text-sm font-semibold rounded-xl hover:border-gray-500 dark:hover:border-gray-400 hover:text-white dark:hover:text-white transition-all duration-200"
        >
          Sign In
        </Link>
      </div>

      {/* Subtle bottom text */}
      <p className="text-gray-600 dark:text-gray-400 text-xs mt-16 text-center">
        © {new Date().getFullYear()} JobRec · Built by Primavat
      </p>
    </div>
  );
}