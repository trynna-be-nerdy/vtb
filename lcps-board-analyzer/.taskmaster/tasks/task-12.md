# Task 12: Frontend setup: Next.js 14, TypeScript, HeroUI, Tailwind, TanStack Query

**Status:** pending
**Priority:** high
**Dependencies:** 10

## Description
Install all frontend dependencies and verify the Next.js app builds cleanly and connects to the FastAPI backend.

## Implementation Details
1. `cd frontend && npm install`
2. Create `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws/updates
   ```
3. Run `npm run dev` and verify http://localhost:3000 loads without errors
4. Fix any TypeScript errors: `npm run type-check`
5. Fix any ESLint errors: `npm run lint`
6. Verify `tailwind.config.ts` includes HeroUI plugin and content paths for all component files
7. Verify `app/providers.tsx` wraps app with HeroUIProvider and QueryClientProvider
8. Verify `app/layout.tsx` includes Navbar and CategoryTicker
9. Test the API client: open browser console on homepage, verify no CORS errors when fetching from FastAPI
10. Verify Inter font loads (check Network tab)
11. Verify dark mode is applied (html element has class='dark')

## Test Strategy
npm install completes with no peer dependency errors. npm run dev starts without errors. Homepage loads at localhost:3000. No TypeScript errors on type-check. No CORS errors in browser console when API is running.
