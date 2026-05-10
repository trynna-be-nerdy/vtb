# Task 13: Homepage and MeetingCard component with real data

**Status:** pending
**Priority:** high
**Dependencies:** 12

## Description
Build out the homepage to display real meeting cards from the API using the masonry grid layout, category navigation, and all card UI details.

## Implementation Details
1. Locate `frontend/app/page.tsx` — verify it calls getMeetings() and getCategories() server-side
2. Verify `frontend/components/cards/MeetingCard.tsx` renders all fields:
   - Source badge (SCHOOL BOARD)
   - Meeting date (formatted: 'May 5, 2026')
   - Title (font-display serif)
   - 2-sentence summary preview (line-clamp-3)
   - Top 2 decisions as bullet list
   - Total items count and fiscal items count
   - External link to source PDF
3. Verify masonry grid CSS (`columns: 1/2/3` at sm/lg breakpoints) in globals.css
4. Verify `CategoryTicker` component auto-scrolls (framer-motion `animate={{ x: ['0%', '-50%'] }}`)
5. Verify `Navbar` renders correctly with frosted glass effect (backdrop-blur-lg)
6. Test on mobile (375px): resize browser, verify nothing overflows
7. Test dark mode colors: background should be #0a0f1e, not pure black
8. Test with 0 meetings (empty state message should show)
9. If ISR revalidation needs to be tested: use `curl -X POST http://localhost:3000/api/revalidate` or just wait 15 min

## Test Strategy
Homepage shows real meeting cards when pipeline has run. Masonry grid has correct column count at each breakpoint. Cards link to correct /meetings/{id} URLs. Category ticker scrolls continuously. Mobile layout renders without horizontal scroll.
