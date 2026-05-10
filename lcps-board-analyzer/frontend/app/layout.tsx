import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import CategoryTicker from "@/components/layout/CategoryTicker";
import Providers from "./providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "LCPS Board Meeting Analyzer",
  description:
    "Gemma 4 reads Loudoun County school board meetings so residents don't have to — plain English summaries, organized by topic.",
  openGraph: {
    title: "LCPS Board Meeting Analyzer",
    description: "Plain English summaries of every LCPS board meeting, organized by topic.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-body bg-navy-900 text-slate-100 min-h-screen`}>
        <Providers>
          <Navbar />
          <CategoryTicker />
          <main className="mx-auto max-w-7xl px-4 sm:px-6 py-8">{children}</main>
          <footer className="border-t border-white/5 mt-16 py-8 text-center text-xs text-slate-600">
            <p>
              Powered by{" "}
              <span className="text-slate-500 font-medium">Gemma 4</span> via Ollama ·{" "}
              <a href="/api/health" className="hover:text-slate-400 transition-colors">
                Pipeline Status
              </a>{" "}
              · Data sourced from official{" "}
              <a href="https://www.lcps.org" target="_blank" rel="noopener noreferrer" className="hover:text-slate-400 transition-colors">
                lcps.org
              </a>{" "}
              and{" "}
              <a href="https://www.loudoun.gov" target="_blank" rel="noopener noreferrer" className="hover:text-slate-400 transition-colors">
                loudoun.gov
              </a>
            </p>
          </footer>
        </Providers>
      </body>
    </html>
  );
}
