import { getMeeting } from "@/lib/api";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ExternalLink, DollarSign, ChevronDown } from "lucide-react";
import { CATEGORY_MAP, URGENCY_STYLES } from "@/lib/constants";

export const revalidate = 0; // Always fresh — invalidated by pipeline after new content

interface Props {
  params: { id: string };
}

export default async function MeetingDetailPage({ params }: Props) {
  let meeting;
  try {
    meeting = await getMeeting(params.id);
  } catch {
    notFound();
  }

  const formattedDate = new Date(meeting.meeting_date).toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="max-w-4xl mx-auto space-y-10">
      {/* Back */}
      <Link href="/" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">
        ← All meetings
      </Link>

      {/* Meeting header */}
      <header className="space-y-4">
        <div className="flex items-center gap-2 text-xs">
          <span className="bg-blue-900/40 text-blue-300 px-2 py-0.5 rounded font-bold tracking-widest uppercase">
            SCHOOL BOARD
          </span>
          <time className="text-slate-500">{formattedDate}</time>
        </div>

        <h1 className="font-display text-2xl sm:text-3xl font-bold text-white leading-tight">
          {meeting.title}
        </h1>

        {meeting.meeting_overview && (
          <p className="text-slate-300 text-base leading-relaxed">{meeting.meeting_overview}</p>
        )}

        {/* Quick stats */}
        <div className="flex flex-wrap gap-4 pt-2 text-sm text-slate-400">
          <span>{meeting.total_items} agenda items</span>
          {meeting.fiscal_items > 0 && (
            <span className="flex items-center gap-1 text-green-400">
              <DollarSign size={14} /> {meeting.fiscal_items} fiscal items
              {meeting.fiscal_total && <> · {meeting.fiscal_total}</>}
            </span>
          )}
          {meeting.source_pdf_url && (
            <a
              href={meeting.source_pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-1 text-slate-500 hover:text-slate-300 transition-colors"
            >
              <ExternalLink size={12} /> Source PDF
            </a>
          )}
        </div>
      </header>

      {/* Top decisions */}
      {meeting.top_decisions && meeting.top_decisions.length > 0 && (
        <section className="bg-navy-800/60 border border-white/10 rounded-xl p-6">
          <h2 className="text-xs font-bold tracking-widest uppercase text-slate-500 mb-4">Top Decisions</h2>
          <ol className="space-y-2">
            {meeting.top_decisions.map((d, i) => (
              <li key={i} className="flex items-start gap-3 text-slate-200 text-sm">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-800 text-blue-200 text-xs flex items-center justify-center font-bold">
                  {i + 1}
                </span>
                {d}
              </li>
            ))}
          </ol>
        </section>
      )}

      {/* Agenda items */}
      <section className="space-y-4">
        <h2 className="text-xs font-bold tracking-widest uppercase text-slate-500">All Agenda Items</h2>

        {meeting.agenda_items.map((item) => {
          const urgency = URGENCY_STYLES[item.urgency] ?? URGENCY_STYLES.routine;
          const cat = CATEGORY_MAP[item.primary_category];

          return (
            <details
              key={item.id}
              className={`group rounded-xl border ${urgency.border} bg-navy-800/60 overflow-hidden`}
            >
              <summary className="flex items-start justify-between gap-4 px-5 py-4 cursor-pointer list-none hover:bg-navy-700/40 transition-colors">
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    {cat && (
                      <span className="text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full"
                        style={{ backgroundColor: `${cat.color}22`, color: cat.color }}>
                        {cat.label}
                      </span>
                    )}
                    {item.fiscal_impact && (
                      <span className="text-[10px] text-green-400 bg-green-900/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                        <DollarSign size={10} /> Fiscal
                      </span>
                    )}
                    <span className={`text-[10px] px-2 py-0.5 rounded-full ${urgency.badge}`}>
                      {urgency.label}
                    </span>
                  </div>
                  <h3 className="font-display font-semibold text-white text-sm sm:text-base leading-snug">
                    {item.title}
                  </h3>
                  <p className="text-slate-400 text-sm mt-1 line-clamp-2">{item.summary}</p>
                </div>
                <ChevronDown size={16} className="flex-shrink-0 mt-1 text-slate-500 group-open:rotate-180 transition-transform" />
              </summary>

              <div className="px-5 pb-5 space-y-4 border-t border-white/5 pt-4">
                <p className="text-slate-300 text-sm leading-relaxed">{item.summary}</p>

                {item.decisions.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Decisions</h4>
                    <ul className="space-y-1">
                      {item.decisions.map((d, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                          <span className="mt-1.5 h-1.5 w-1.5 bg-blue-400 rounded-full flex-shrink-0" />
                          {d}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.action_items.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Next Steps</h4>
                    <ul className="space-y-1">
                      {item.action_items.map((a, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-slate-400">
                          <span className="mt-1.5 h-1.5 w-1.5 bg-amber-400 rounded-full flex-shrink-0" />
                          {a}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {item.source_pdf_url && (
                  <a
                    href={item.source_pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-300 transition-colors"
                  >
                    <ExternalLink size={11} />
                    View in source PDF{item.page_range ? ` · ${item.page_range}` : ""}
                  </a>
                )}
              </div>
            </details>
          );
        })}
      </section>
    </div>
  );
}
