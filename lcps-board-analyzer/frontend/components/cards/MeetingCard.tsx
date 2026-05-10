"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { DollarSign, ExternalLink, FileText } from "lucide-react";
import { CATEGORY_MAP, URGENCY_STYLES } from "@/lib/constants";
import type { MeetingCard as MeetingCardType } from "@/types";

interface Props {
  meeting: MeetingCardType;
}

export default function MeetingCard({ meeting }: Props) {
  const urgencyStyle = URGENCY_STYLES[meeting.processing_status as keyof typeof URGENCY_STYLES] ?? URGENCY_STYLES.routine;

  const formattedDate = new Date(meeting.meeting_date).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <motion.div
      whileHover={{ y: -2 }}
      transition={{ type: "spring", stiffness: 400, damping: 30 }}
      className={`group relative flex flex-col rounded-xl border ${urgencyStyle.border} bg-navy-800/80 backdrop-blur-sm p-5 hover:bg-navy-700/80 transition-colors`}
    >
      {/* Source + date row */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-[10px] font-bold tracking-widest uppercase text-blue-400 bg-blue-900/40 px-2 py-0.5 rounded">
          SCHOOL BOARD
        </span>
        <time className="text-xs text-slate-500">{formattedDate}</time>
      </div>

      {/* Title */}
      <Link href={`/meetings/${meeting.id}`}>
        <h2 className="font-display text-white font-semibold text-base leading-snug mb-2 group-hover:text-blue-300 transition-colors line-clamp-3">
          {meeting.title}
        </h2>
      </Link>

      {/* Overview */}
      {meeting.meeting_overview && (
        <p className="text-slate-400 text-sm leading-relaxed line-clamp-3 mb-4">
          {meeting.meeting_overview}
        </p>
      )}

      {/* Top decisions */}
      {meeting.top_decisions && meeting.top_decisions.length > 0 && (
        <ul className="mb-4 space-y-1">
          {meeting.top_decisions.slice(0, 2).map((decision, i) => (
            <li key={i} className="flex items-start gap-2 text-xs text-slate-300">
              <span className="mt-0.5 h-1.5 w-1.5 rounded-full bg-blue-400 flex-shrink-0" />
              {decision}
            </li>
          ))}
        </ul>
      )}

      {/* Footer stats */}
      <div className="mt-auto flex items-center justify-between pt-3 border-t border-white/5">
        <div className="flex items-center gap-3 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <FileText size={12} />
            {meeting.total_items} items
          </span>
          {meeting.fiscal_items > 0 && (
            <span className="flex items-center gap-1 text-green-400">
              <DollarSign size={12} />
              {meeting.fiscal_items} fiscal
            </span>
          )}
        </div>
        <Link
          href={meeting.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-500 hover:text-slate-300 transition-colors"
          onClick={(e) => e.stopPropagation()}
          aria-label="View source PDF"
        >
          <ExternalLink size={12} />
        </Link>
      </div>
    </motion.div>
  );
}
