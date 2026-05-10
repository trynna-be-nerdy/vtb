"use client";

import Link from "next/link";
import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import { Search, Sun, Moon } from "lucide-react";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { WebSocketMessage } from "@/types";

export default function Navbar() {
  const [dark, setDark] = useState(true);
  const [toast, setToast] = useState<string | null>(null);

  const handleWsMessage = useCallback((msg: WebSocketMessage) => {
    if (msg.type === "new_item") {
      setToast("New board meeting content published — refresh to see it");
      setTimeout(() => setToast(null), 6000);
    }
  }, []);

  useWebSocket(handleWsMessage);

  return (
    <>
      {/* Frosted glass sticky navbar */}
      <nav className="sticky top-0 z-50 border-b border-white/10 backdrop-blur-lg bg-navy-900/80">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <span className="text-blue-400 font-bold text-sm tracking-widest uppercase">LCPS</span>
            <span className="text-white font-display font-semibold text-lg leading-tight">
              Board Analyzer
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link
              href="/search"
              className="flex items-center gap-1.5 text-slate-400 hover:text-white text-sm transition-colors"
              aria-label="Search"
            >
              <Search size={16} />
              <span className="hidden sm:inline">Search</span>
              <kbd className="hidden sm:inline ml-1 px-1.5 py-0.5 text-xs bg-white/10 rounded text-slate-400">
                ⌘K
              </kbd>
            </Link>

            <button
              onClick={() => setDark((d) => !d)}
              className="text-slate-400 hover:text-white transition-colors"
              aria-label="Toggle dark mode"
            >
              {dark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Live toast notification */}
      {toast && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className="fixed top-20 right-4 z-50 bg-blue-600 text-white px-4 py-3 rounded-lg shadow-xl text-sm max-w-xs"
        >
          🔴 {toast}
        </motion.div>
      )}
    </>
  );
}
