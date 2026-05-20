"""Search lcps.org for Board of Education meeting documents."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Search the lcps.org sitemap or main nav for board meetings
        search_urls = [
            "https://www.lcps.org",
            "https://www.lcps.org/about/board-of-education",
            "https://www.lcps.org/about/board-of-education/meetings",
            "https://www.lcps.org/board",
            "https://www.lcps.org/domain/6",
        ]

        for url in search_urls:
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(2000)
                status = resp.status if resp else "?"
                title = await page.title()
                print(f"\n{url}")
                print(f"  status={status}  title={title!r}")

                # Find board-related links
                links = await page.query_selector_all("a")
                for link in links:
                    href = (await link.get_attribute("href") or "")
                    txt = (await link.inner_text()).strip()[:60]
                    if any(x in txt.lower() or x in href.lower() for x in ["board of education", "board meeting", "agenda", "school board", "minutes", "boarddocs", "diligent"]):
                        print(f"  LINK: {txt!r} -> {href!r}")

            except Exception as e:
                print(f"\n{url} -> {type(e).__name__}: {str(e)[:80]}")

        # Also try the search
        try:
            await page.goto("https://www.lcps.org/search?q=board+of+education+meetings+agenda", wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(2000)
            print(f"\nSearch results:")
            body = (await page.inner_text("body"))[:1000].replace("\n", "  ").strip()
            print(f"  {body!r}")
        except Exception as e:
            print(f"Search failed: {e}")

        await browser.close()


asyncio.run(main())
