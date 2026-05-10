import { getMeetings, getCategories } from "@/lib/api";
import MeetingCard from "@/components/cards/MeetingCard";
import Link from "next/link";
import { CATEGORIES } from "@/lib/constants";
import { ChevronRight } from "lucide-react";

export const revalidate = 900; // ISR — regenerate every 15 min

export default async function HomePage() {
  const [meetingsData, categories] = await Promise.all([
    getMeetings(1, 12),
    getCategories(),
  ]);

  const categoryCountMap = Object.fromEntries(categories.map((c) => [c.slug, c.item_count]));

  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center py-8 space-y-4">
        <div className="inline-block bg-blue-900/40 text-blue-300 text-xs font-bold tracking-widest uppercase px-3 py-1 rounded-full border border-blue-700/50">
          Gemma 4 Good Hackathon · Digital Equity
        </div>
        <h1 className="font-display text-3xl sm:text-4xl lg:text-5xl font-bold text-white leading-tight max-w-3xl mx-auto">
          What did the school board decide this week?
        </h1>
        <p className="text-slate-400 text-lg max-w-xl mx-auto">
          Gemma 4 reads every official LCPS board document and rewrites it in plain English — so you can understand what was decided in 2 minutes instead of 2 hours.
        </p>
      </section>

      {/* Category grid */}
      <section>
        <h2 className="text-xs font-bold tracking-widest uppercase text-slate-500 mb-4">Browse by Topic</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {CATEGORIES.map((cat) => (
            <Link
              key={cat.slug}
              href={`/category/${cat.slug}`}
              className="group flex items-center justify-between rounded-lg border border-white/10 bg-navy-800/60 px-4 py-3 hover:border-white/20 hover:bg-navy-700/60 transition-all"
            >
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full flex-shrink-0" style={{ backgroundColor: cat.color }} />
                <span className="text-sm text-slate-300 group-hover:text-white transition-colors">{cat.label}</span>
              </div>
              <div className="flex items-center gap-1">
                <span className="text-xs text-slate-600">{categoryCountMap[cat.slug] ?? 0}</span>
                <ChevronRight size={12} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Meeting cards — masonry grid */}
      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xs font-bold tracking-widest uppercase text-slate-500">Latest Meetings</h2>
          <span className="text-xs text-slate-600">{meetingsData.total} total</span>
        </div>

        {meetingsData.items.length === 0 ? (
          <div className="text-center py-16 text-slate-500">
            <p className="text-lg mb-2">No meetings processed yet.</p>
            <p className="text-sm">The pipeline runs every 6 hours — check back soon.</p>
          </div>
        ) : (
          <div className="masonry-grid">
            {meetingsData.items.map((meeting) => (
              <div key={meeting.id} className="masonry-item">
                <MeetingCard meeting={meeting} />
              </div>
            ))}
          </div>
        )}

        {meetingsData.has_next && (
          <div className="text-center mt-8">
            <Link
              href="/meetings"
              className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white border border-white/10 px-4 py-2 rounded-lg hover:border-white/20 transition-all"
            >
              View all meetings <ChevronRight size={14} />
            </Link>
          </div>
        )}
      </section>
    </div>
  );
}
