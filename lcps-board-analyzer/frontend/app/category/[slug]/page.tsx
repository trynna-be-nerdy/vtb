import { getCategoryFeed, getCategories } from "@/lib/api";
import { notFound } from "next/navigation";
import Link from "next/link";
import { ExternalLink, DollarSign } from "lucide-react";
import { CATEGORY_MAP, URGENCY_STYLES } from "@/lib/constants";

export const revalidate = 900;

interface Props {
  params: { slug: string };
}

export async function generateStaticParams() {
  const categories = await getCategories();
  return categories.map((c) => ({ slug: c.slug }));
}

export default async function CategoryPage({ params }: Props) {
  const cat = CATEGORY_MAP[params.slug as keyof typeof CATEGORY_MAP];
  if (!cat) notFound();

  const feed = await getCategoryFeed(params.slug, 1, 20);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <Link href="/" className="text-sm text-slate-500 hover:text-slate-300 transition-colors">
        ← Home
      </Link>

      {/* Category header */}
      <header className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="h-3 w-3 rounded-full" style={{ backgroundColor: cat.color }} />
          <span className="text-xs font-bold tracking-widest uppercase text-slate-500">
            {cat.description}
          </span>
        </div>
        <h1 className="font-display text-3xl font-bold text-white">{cat.label}</h1>
        <p className="text-slate-400 text-sm">
          {feed.total} agenda items · updated automatically every 6 hours
        </p>
      </header>

      {/* Item feed */}
      <div className="space-y-4">
        {feed.items.length === 0 ? (
          <p className="text-slate-500 text-center py-16">No items in this category yet.</p>
        ) : (
          feed.items.map((item) => {
            const urgency = URGENCY_STYLES[item.urgency] ?? URGENCY_STYLES.routine;
            return (
              <article
                key={item.id}
                className={`rounded-xl border ${urgency.border} bg-navy-800/60 p-5 space-y-3`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${urgency.badge}`}>
                    {urgency.label}
                  </span>
                  {item.fiscal_impact && (
                    <span className="text-[10px] text-green-400 bg-green-900/30 px-2 py-0.5 rounded-full flex items-center gap-1">
                      <DollarSign size={10} /> Fiscal
                    </span>
                  )}
                  {item.secondary_tags.slice(0, 3).map((tag) => (
                    <span key={tag} className="text-[10px] text-slate-500 bg-white/5 px-2 py-0.5 rounded-full">
                      {tag}
                    </span>
                  ))}
                </div>

                <h2 className="font-display font-semibold text-white text-base leading-snug">
                  {item.title}
                </h2>

                <p className="text-slate-400 text-sm leading-relaxed">{item.summary}</p>

                {item.decisions.length > 0 && (
                  <ul className="space-y-1">
                    {item.decisions.slice(0, 2).map((d, i) => (
                      <li key={i} className="flex items-start gap-2 text-xs text-slate-400">
                        <span className="mt-1.5 h-1 w-1 bg-blue-400 rounded-full flex-shrink-0" />
                        {d}
                      </li>
                    ))}
                  </ul>
                )}

                {item.source_pdf_url && (
                  <a
                    href={item.source_pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-slate-600 hover:text-slate-400 transition-colors"
                  >
                    <ExternalLink size={11} /> Source
                  </a>
                )}
              </article>
            );
          })
        )}
      </div>
    </div>
  );
}
