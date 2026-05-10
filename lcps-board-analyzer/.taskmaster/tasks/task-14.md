# Task 14: Meeting detail page, category pages, and search page

**Status:** pending
**Priority:** high
**Dependencies:** 13

## Description
Implement and verify the three inner pages: meeting detail with accordion, category feed with filters, and debounced search.

## Implementation Details
1. **Meeting detail page** (`/meetings/[id]`):
   - Verify back navigation link works
   - Verify meeting_overview, top_decisions, quick stats all render
   - Verify expandable `<details>` accordion for each agenda_item
   - Inside accordion: full summary, decisions list, action_items list, source PDF link with page_range
   - Test with a meeting that has fiscal_items > 0 (fiscal total should show)
   - Test 404 behavior: visit /meetings/non-existent-id

2. **Category pages** (`/category/[slug]`):
   - Verify all 12 slugs resolve to a page (`generateStaticParams` returns them all)
   - Verify items display with correct urgency border color
   - Verify secondary_tags appear as chips
   - Test fiscal_only filter: add `?fiscal_only=true` to URL (may need query param wiring)
   - Test empty category (no items yet): shows 'No items in this category yet.'

3. **Search page** (`/search`):
   - Verify debouncing: type quickly, only one API call fires after 400ms
   - Verify results appear with category chip and urgency border
   - Verify 0 results shows 'No results found.'
   - Verify query shorter than 2 chars shows no results (no API call)
   - Test keyboard: pressing Enter should not submit a form

## Test Strategy
Meeting detail page loads with all accordion items for a real meeting. Each of the 12 category pages loads without 404. Search returns results for a keyword present in real data. Debounce prevents API calls on every keystroke.
