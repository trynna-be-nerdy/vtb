"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { CATEGORIES } from "@/lib/constants";

// Duplicate the list so the scroll loop is seamless
const DOUBLED = [...CATEGORIES, ...CATEGORIES];

export default function CategoryTicker() {
  return (
    <div className="overflow-hidden border-b border-white/10 bg-navy-800/60 py-2">
      <motion.div
        className="flex gap-6 whitespace-nowrap"
        animate={{ x: ["0%", "-50%"] }}
        transition={{ duration: 40, ease: "linear", repeat: Infinity }}
      >
        {DOUBLED.map((cat, i) => (
          <Link
            key={`${cat.slug}-${i}`}
            href={`/category/${cat.slug}`}
            className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
          >
            <span
              className="inline-block h-2 w-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: cat.color }}
            />
            {cat.label}
          </Link>
        ))}
      </motion.div>
    </div>
  );
}
