"""Find LCPS board meeting documents."""
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

        urls = [
            "https://www.lcps.org/boardofed",
            "https://go.boarddocs.com/va/lcps/Board.nsf/Public?open",
            "https://www.lcps.org/Page/17",
            "https://www.lcps.org/Page/6",
        ]

        for url in urls:
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)
                title = await page.title()
                body = (await page.inner_text("body"))[:400].replace("\n", " ").strip()
                status = resp.status if resp else "no_resp"
                print(f"\n{url}")
                print(f"  status={status}  title={title!r}")
                print(f"  body={body[:200]!r}")

                links = await page.query_selector_all("a")
                for link in links[:30]:
                    href = (await link.get_attribute("href") or "")
                    txt = (await link.inner_text()).strip()[:60]
                    if any(x in href.lower() or x in txt.lower() for x in ["agenda", "pdf", "board", "meeting", "minutes", "packet", "document"]):
                        print(f"  LINK: {txt!r} -> {href!r}")
            except Exception as e:
                print(f"\n{url} -> ERROR: {type(e).__name__}: {str(e)[:100]}")

        await browser.close()


asyncio.run(main())
