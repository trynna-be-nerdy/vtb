"""Debug scraper pages to find correct selectors."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def debug_loudoun():
    print("=== LOUDOUN LEGISTAR ===")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://loudoun.legistar.com/Calendar.aspx", wait_until="networkidle")

        tables = await page.query_selector_all("table")
        print(f"Tables: {len(tables)}")
        for i, t in enumerate(tables[:8]):
            cls = (await t.get_attribute("class") or "")[:50]
            tid = (await t.get_attribute("id") or "")[:50]
            rows = await t.query_selector_all("tr")
            print(f"  [{i}] id={tid} class={cls} rows={len(rows)}")

        print("\nAll links containing 'MeetingDetail' or 'agenda':")
        links = await page.query_selector_all("a")
        for link in links[:30]:
            href = (await link.get_attribute("href") or "")
            txt = (await link.inner_text()).strip()[:60]
            if "detail" in href.lower() or "agenda" in txt.lower() or "pdf" in href.lower():
                print(f"  {txt!r}  ->  {href!r}")

        print("\nFirst 8 table rows (any table):")
        rows = await page.query_selector_all("tr")
        for r in rows[1:9]:
            txt = (await r.inner_text()).replace("\t", " ").replace("\n", " ").strip()[:120]
            print(f"  {txt!r}")

        await browser.close()


async def debug_boarddocs():
    print("\n=== BOARDDOCS LCPS ===")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124"
        )
        page = await context.new_page()
        await page.goto("https://go.boarddocs.com/va/lcps/Board.nsf/Public", wait_until="networkidle")

        print(f"URL after load: {page.url}")
        print(f"Title: {await page.title()}")

        # Wait a bit for JS
        await page.wait_for_timeout(3000)

        # Look for any meeting-related content
        body_text = (await page.inner_text("body"))[:1000]
        print(f"Body text (first 1000):\n{body_text}")

        links = await page.query_selector_all("a")
        print(f"\nLinks ({len(links)} total) — first 20:")
        for link in links[:20]:
            href = (await link.get_attribute("href") or "")[:80]
            txt = (await link.inner_text()).strip()[:50]
            if txt:
                print(f"  {txt!r} -> {href!r}")

        await browser.close()


async def main():
    await debug_loudoun()
    await debug_boarddocs()


asyncio.run(main())
