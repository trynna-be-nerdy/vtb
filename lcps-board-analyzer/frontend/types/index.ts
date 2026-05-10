// ─── API Response Types ───────────────────────────────────────────────────────

export interface KeyFigures {
  amounts: string[];
  vote_tallies: string[];
  dates: string[];
  schools: string[];
}

export interface AgendaItem {
  id: string;
  meeting_id: string;
  item_order: number;
  title: string;
  summary: string;
  decisions: string[];
  action_items: string[];
  key_figures: KeyFigures;
  primary_category: string;
  secondary_tags: string[];
  urgency: "routine" | "notable" | "significant";
  fiscal_impact: boolean;
  affects_schools: string[];
  source_pdf_url: string | null;
  page_range: string | null;
  created_at: string;
}

export interface SupportingDocument {
  id: string;
  title: string;
  document_type: string;
  url: string;
  summary: string | null;
}

export interface MeetingCard {
  id: string;
  title: string;
  meeting_date: string;
  source_url: string;
  meeting_overview: string | null;
  top_decisions: string[] | null;
  fiscal_total: string | null;
  total_items: number;
  fiscal_items: number;
  processing_status: string;
  created_at: string;
}

export interface MeetingDetail extends MeetingCard {
  next_meeting_notes: string | null;
  agenda_items: AgendaItem[];
  supporting_documents: SupportingDocument[];
}

export interface PaginatedMeetings {
  items: MeetingCard[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface Category {
  slug: string;
  label: string;
  description: string;
  item_count: number;
  recent_activity_overview?: string | null;
}

export interface CategoryFeed {
  category: Category;
  items: AgendaItem[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
}

export interface SearchResult {
  items: AgendaItem[];
  total: number;
  query: string;
}

export interface HealthStatus {
  status: string;
  last_run_at: string | null;
  last_run_status: string | null;
  items_processed_last_run: number | null;
  total_meetings: number;
  total_agenda_items: number;
  pipeline_queue_depth: number;
}

// ─── UI Types ─────────────────────────────────────────────────────────────────

export type UrgencyLevel = "routine" | "notable" | "significant";

export interface WebSocketMessage {
  type: "new_item";
  meeting_id: string;
  category: string;
  timestamp: string;
}
