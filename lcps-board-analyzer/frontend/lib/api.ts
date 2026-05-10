/**
 * API client — thin wrapper around fetch pointing at the FastAPI backend.
 * All functions return typed responses from types/index.ts.
 */
import type {
  PaginatedMeetings,
  MeetingDetail,
  Category,
  CategoryFeed,
  SearchResult,
  HealthStatus,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string, params?: Record<string, string | number | boolean>): Promise<T> {
  const url = new URL(`${BASE_URL}${path}`);
  if (params) {
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, String(v)));
  }
  const res = await fetch(url.toString(), { next: { revalidate: 900 } }); // 15-min ISR
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

// ─── Meetings ─────────────────────────────────────────────────────────────────

export const getMeetings = (page = 1, pageSize = 20) =>
  apiFetch<PaginatedMeetings>("/api/meetings", { page, page_size: pageSize });

export const getMeeting = (id: string) =>
  apiFetch<MeetingDetail>(`/api/meetings/${id}`);

// ─── Categories ───────────────────────────────────────────────────────────────

export const getCategories = () =>
  apiFetch<Category[]>("/api/categories");

export const getCategoryFeed = (slug: string, page = 1, pageSize = 20, fiscalOnly = false) =>
  apiFetch<CategoryFeed>(`/api/categories/${slug}`, {
    page,
    page_size: pageSize,
    fiscal_only: fiscalOnly,
  });

// ─── Search ───────────────────────────────────────────────────────────────────

export const searchItems = (q: string, page = 1, pageSize = 20) =>
  apiFetch<SearchResult>("/api/search", { q, page, page_size: pageSize });

// ─── Health ───────────────────────────────────────────────────────────────────

export const getHealth = () =>
  apiFetch<HealthStatus>("/api/health");
