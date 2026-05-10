"use client";

import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { searchItems } from "@/lib/api";
import { CATEGORY_MAP, URGENCY_STYLES } from "@/lib/constants";
import { useDebounce } from "@/hooks/useDebounce";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebounce(query, 400);

  const { data, isLoading } = useQuery({
    queryKey: ["search", debouncedQuery],
    queryFn: () => searchItems(debouncedQuery),
    enabled: debouncedQuery.length >= 2,
  });

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <h1 className="font-display text-2xl font-bold text-white">Search board meetings</h1>

      <div className="relative">
        <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          autoFocus
          type="search"
          placeholder="Search decisions, topics, schools…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full bg-navy-800/80 border border-white/10 rounded-xl pl-11 pr-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors text-base"
        />
      </div>

      {isLoading && (
        <div className="text-slate-500 text-sm text-center py-8 animate-pulse">Searching…</div>
      )}

      {data && (
        <div className="space-y-4">
          <p className="text-xs text-slate-600">{data.total} results for &ldquo;{data.query}&rdquo;</p>
          {data.items.map((item) => {
            const urgency = URGENCY_STYLES[item.urgency] ?? URGENCY_STYLES.routine;
            const cat = CATEGORY_MAP[item.primary_category as keyof typeof CATEGORY_MAP];
            return (
              <article key={item.id} className={`rounded-xl border ${urgency.border} bg-navy-800/60 p-5 space-y-2`}>
                {cat && (
                  <span className="text-[10px] font-bold tracking-widest uppercase px-2 py-0.5 rounded-full"
                    style={{ backgroundColor: `${cat.color}22`, color: cat.color }}>
                    {cat.label}
                  </span>
                )}
                <h2 className="font-display font-semibold text-white text-sm">{item.title}</h2>
                <p className="text-slate-400 text-sm leading-relaxed">{item.summary}</p>
              </article>
            );
          })}
        </div>
      )}

      {!isLoading && debouncedQuery.length >= 2 && data?.total === 0 && (
        <p className="text-center text-slate-500 py-12">No results found.</p>
      )}
    </div>
  );
}
