// Mirrors backend/api/schemas.py Pydantic models

export interface Pagination {
  page: number
  limit: number
  total: number
  has_next: boolean
}

export interface AgendaItemCard {
  id: number
  meeting_id: number
  title: string
  summary: string
  primary_category: string
  secondary_tags: string[] | null
  urgency: string
  fiscal_impact: boolean
  affects_schools: string[] | null
  source_pdf_url: string | null
  page_range: string | null
  created_at: string
  board_slug?: string
  meeting_date?: string
}

export interface AgendaItemDetail extends AgendaItemCard {
  decisions: string[] | null
  action_items: string[] | null
  key_figures: Record<string, unknown> | null
}

export interface MeetingCard {
  id: number
  title: string
  board_slug: string
  meeting_date: string
  meeting_overview: string | null
  top_decisions: string[] | null
  fiscal_total: string | null
  total_items: number
  fiscal_items: number
  processing_status: string
}

export interface SupportingDocument {
  id: number
  title: string | null
  url: string
  doc_type: string | null
}

export interface MeetingDetail extends MeetingCard {
  source_url: string | null
  source_pdf_url: string | null
  next_meeting_notes: string | null
  agenda_items: AgendaItemDetail[]
  supporting_documents: SupportingDocument[]
  updated_at: string
}

export interface MeetingListResponse {
  meetings: MeetingCard[]
  pagination: Pagination
}

export interface MeetingDetailResponse {
  meeting: MeetingDetail
}

export interface CategoryInfo {
  slug: string
  label: string
  item_count: number
}

export interface CategoryListResponse {
  categories: CategoryInfo[]
}

export interface SearchResult extends AgendaItemCard {
  meeting_title: string
  meeting_date: string
  board_slug: string
  rank: number
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  pagination: Pagination
}

export interface HealthResponse {
  status: string
  last_pipeline_run: string | null
  last_pipeline_status: string | null
  items_this_month: number
  queue_depth: number
}

// UI-level board config
export interface BoardConfig {
  slug: string
  title: string
  meta: string
  dot: 'teal' | 'amber' | 'blue' | 'purple'
  limit: number
  isAdvisory?: boolean
}

export const BOARD_CONFIGS: BoardConfig[] = [
  {
    slug: 'board-of-supervisors',
    title: 'Board of Supervisors',
    meta: 'Central county governing body — budget, taxes, land use, and major policy decisions · Meets 1st & 3rd Tuesday',
    dot: 'teal',
    limit: 3,
  },
  {
    slug: 'planning-commission',
    title: 'Planning Commission',
    meta: 'Controls zoning, rezoning, and development approvals — key for housing, commercial growth, and infrastructure decisions · Monthly hearings',
    dot: 'amber',
    limit: 3,
  },
  {
    slug: 'lcps-school-board',
    title: 'LCPS School Board',
    meta: 'Education policy, budget, curriculum, and facilities decisions — published separately through LCPS · Meets 2nd & 4th Tuesday',
    dot: 'blue',
    limit: 3,
  },
  {
    slug: 'advisory-boards',
    title: 'Advisory Boards, Commissions & Standing Committees',
    meta: 'Smaller bodies covering parks, libraries, transportation, and public safety — recommendations often influence full Board of Supervisors votes',
    dot: 'purple',
    limit: 4,
    isAdvisory: true,
  },
]
