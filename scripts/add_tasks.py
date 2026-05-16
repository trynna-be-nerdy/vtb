import json

with open('C:/Users/sriva/VtB/.taskmaster/tasks/tasks.json', 'r') as f:
    data = json.load(f)

tasks = data['master']['tasks']
max_id = max(int(t['id']) for t in tasks)

new_tasks = [
    {
        'id': str(max_id + 1),
        'title': 'Build Official Calendar Page',
        'description': 'Create /calendar page showing all upcoming and past meetings in a monthly calendar view, filterable by board, with color-coded board badges and links to meeting detail pages.',
        'details': (
            '1. Add getMeetingsByMonth(year, month, board?) to frontend/lib/data.ts\n'
            '2. Create app/calendar/page.tsx as a server component\n'
            '3. Add CalendarGrid client component with month navigation\n'
            '4. Color-code each board: BOS=red, Planning=amber, LCPS=green, Advisory=gray\n'
            '5. Each day cell shows meeting badges linking to /meetings/[id]\n'
            '6. Mobile: collapse to list view\n'
            '7. Board filter tabs at top (All, BOS, Planning, LCPS, Advisory)\n'
            '8. Mark today date visually\n'
            '9. Style using existing CSS variables'
        ),
        'testStrategy': 'Verify calendar renders correct days. Test month navigation. Verify meetings on correct dates. Test board filter. Check mobile layout.',
        'priority': 'high',
        'status': 'pending',
        'dependencies': ['8'],
        'subtasks': []
    },
    {
        'id': str(max_id + 2),
        'title': 'Fix Sidebar Navigation - Add All 12 Categories',
        'description': 'Sidebar currently shows only 6 of 12 categories. Add missing 6 with proper labels.',
        'details': (
            '1. Open frontend/components/Sidebar.tsx\n'
            '2. Add missing categories: school-construction, equity-inclusion, technology, community-parks, personnel, general\n'
            '3. Match CATEGORY_LABELS map in lib/data.ts\n'
            '4. Match existing link styling\n'
            '5. Consider a show-more toggle if list is too long'
        ),
        'testStrategy': 'Verify all 12 categories link to /categories/[slug]. Check active state. Test on mobile.',
        'priority': 'medium',
        'status': 'pending',
        'dependencies': ['8'],
        'subtasks': []
    },
    {
        'id': str(max_id + 3),
        'title': 'Make Gemma 4 Ollama Pipeline Operational End-to-End',
        'description': 'Verify the TypeScript pipeline correctly calls Ollama with gemma4:4b, processes a real PDF, writes to PostgreSQL, and publishes to Redis. Fix any issues found.',
        'details': (
            '1. Check frontend/lib/llm.ts - verify Ollama API call format\n'
            '2. Verify OLLAMA_BASE_URL env var is set and Ollama is reachable\n'
            '3. Run test pipeline via POST /api/pipeline/trigger\n'
            '4. Fix common issues: model name mismatch, JSON schema format, PDF extractor errors, scraper 0-doc returns\n'
            '5. If all docs already seen, delete from seen_documents to force reprocessing\n'
            '6. Verify data appears in /meetings, /categories, /search\n'
            '7. Check Redis pub/sub fires (LiveUpdateToast appears)'
        ),
        'testStrategy': 'Trigger pipeline and verify: 1+ meeting in DB, agenda_items inserted, categories populated, health shows updated last_run.',
        'priority': 'high',
        'status': 'pending',
        'dependencies': ['16'],
        'subtasks': []
    },
    {
        'id': str(max_id + 4),
        'title': 'Populate Live Data and Verify All Pages Display Real Content',
        'description': 'After pipeline is working, ensure every page shows real scraped and AI-processed data. Fix any display issues.',
        'details': (
            '1. Run full pipeline and verify DB has real meetings + agenda_items\n'
            '2. Check each page: home, /boards/[slug], /categories/[slug], /meetings/[id], /search, /calendar\n'
            '3. Fix data shape mismatches between DB schema and TypeScript types\n'
            '4. Verify pagination works with real data\n'
            '5. Check health page shows correct stats\n'
            '6. Fix any null field crashes or missing fallbacks'
        ),
        'testStrategy': 'Manual verification of all page routes with real data. Check browser console for errors. No 500 errors in server logs.',
        'priority': 'high',
        'status': 'pending',
        'dependencies': [str(max_id + 3)],
        'subtasks': []
    },
    {
        'id': str(max_id + 5),
        'title': 'Wire Up All Frontend Routes and Fix Navigation Gaps',
        'description': 'Audit every link in Navbar, Sidebar, Footer, and page components. Ensure all links resolve. Test full navigation flow end-to-end.',
        'details': (
            '1. Sidebar: Today, Calendar, Search, 4 boards, 12 categories, 2 external sources\n'
            '2. Footer: About, Data Sources, AI Transparency, Contact\n'
            '3. Home: board sections -> /boards/[slug], meeting cards -> /meetings/[id]\n'
            '4. Board pages: meeting cards -> /meetings/[id], pagination\n'
            '5. Category pages: source PDF links, pagination\n'
            '6. Meeting detail: back link, accordion expand\n'
            '7. Search: results link to correct pages\n'
            '8. Test 404 for missing IDs and invalid slugs\n'
            '9. Verify sidebar active states by route\n'
            '10. External links open in new tab'
        ),
        'testStrategy': 'Click every nav link. No 404s in network tab. Test invalid routes. Test 404 page.',
        'priority': 'medium',
        'status': 'pending',
        'dependencies': [str(max_id + 1)],
        'subtasks': []
    }
]

for t in new_tasks:
    tasks.append(t)

data['master']['tasks'] = tasks

with open('C:/Users/sriva/VtB/.taskmaster/tasks/tasks.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'Added {len(new_tasks)} tasks. IDs: {[t["id"] for t in new_tasks]}')
