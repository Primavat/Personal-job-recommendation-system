import type { Metadata } from "next";
import "@/app/globals.css";
import Providers from "./providers";

export const metadata: Metadata = {
  title: "JobRec - AI-Powered Job Recommendations",
  description: "Find your perfect tech job with AI-powered recommendations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-white dark:bg-gray-950">
        <Providers>
          <main className="flex-1">
            {children}
          </main>
          <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 mt-auto">
            <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                © {new Date().getFullYear()} JobRec. All rights reserved.
              </span>
              <span className="text-sm text-gray-600 dark:text-gray-400">
                Built by <span className="text-gray-900 dark:text-white font-medium">Primavat</span>
              </span>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  );
}