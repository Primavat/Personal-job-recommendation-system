import type { Metadata } from "next";
import "@/app/globals.css";

export const metadata: Metadata = {
  title: "JobRec - AI-Powered Job Recommendations",
  description: "Find your perfect tech job with AI-powered recommendations",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-gray-50">
        <main className="flex-1">
          {children}
        </main>
        <footer className="border-t border-gray-200 bg-white mt-auto">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <span className="text-sm text-gray-400">
              © {new Date().getFullYear()} JobRec. All rights reserved.
            </span>
            <span className="text-sm text-gray-400">
              Built by <span className="text-gray-600 font-medium">Pranav</span>
            </span>
          </div>
        </footer>
      </body>
    </html>
  );
}