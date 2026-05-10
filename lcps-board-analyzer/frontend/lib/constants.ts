// ─── The 12 content categories ────────────────────────────────────────────────

export const CATEGORIES = [
  { slug: "schools-education",  label: "Schools & Education",  description: "Curriculum, testing, calendars, special ed",    color: "#3b82f6" },
  { slug: "school-construction", label: "School Construction",  description: "New buildings, renovations, CIP projects",       color: "#f59e0b" },
  { slug: "budget-finance",      label: "Budget & Finance",     description: "Budgets, audits, grants, debt, fiscal votes",    color: "#10b981" },
  { slug: "transportation",      label: "Transportation",        description: "Buses, VDOT, roads, sidewalks, traffic",         color: "#8b5cf6" },
  { slug: "zoning-land-use",     label: "Zoning & Land Use",    description: "Rezonings, special exceptions, proffering",      color: "#ef4444" },
  { slug: "public-safety",       label: "Public Safety",        description: "Safety protocols, SRO, emergency plans",         color: "#f97316" },
  { slug: "policy-governance",   label: "Policy & Governance",  description: "Board policy, ethics, appointments",             color: "#06b6d4" },
  { slug: "equity-inclusion",    label: "Equity & Inclusion",   description: "Title IX, language access, equity audits",       color: "#ec4899" },
  { slug: "technology",          label: "Technology",           description: "EdTech, cybersecurity, FERPA, AI policy",        color: "#6366f1" },
  { slug: "community-parks",     label: "Community & Parks",    description: "Facility use, afterschool, parks",               color: "#84cc16" },
  { slug: "personnel",           label: "Personnel",            description: "Staff, compensation, labor agreements",           color: "#a78bfa" },
  { slug: "general",             label: "General",              description: "Catch-all for unclassified items",               color: "#94a3b8" },
] as const;

export const CATEGORY_MAP = Object.fromEntries(CATEGORIES.map((c) => [c.slug, c]));

export type CategorySlug = (typeof CATEGORIES)[number]["slug"];

// ─── Urgency styling ─────────────────────────────────────────────────────────

export const URGENCY_STYLES = {
  routine:     { border: "border-slate-600",   badge: "bg-slate-700 text-slate-200",  label: "Routine"     },
  notable:     { border: "border-amber-500",   badge: "bg-amber-900 text-amber-200",  label: "Notable"     },
  significant: { border: "border-red-500",     badge: "bg-red-900   text-red-200",    label: "Significant" },
} as const;

// ─── Source badge styles ─────────────────────────────────────────────────────

export const SOURCE_BADGES = {
  lcps:        { label: "SCHOOL BOARD", className: "bg-blue-900  text-blue-200"  },
  loudoun_bos: { label: "COUNTY",       className: "bg-green-900 text-green-200" },
} as const;
