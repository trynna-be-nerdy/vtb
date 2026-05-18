"""Find actual API endpoints used by both portals."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def debug_loudoun_network():
    print("=== LOUDOUN — intercepting network requests ===")
    api_calls = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        # Intercept all network requests
        async def on_request(req):
            url = req.url
            if any(x in url for x in ["legistar", "loudoun", "api", "json", "calendar", "event"]):
                api_calls.append(f"{req.method} {url}")

        page.on("request", on_request)

        await page.goto("https://loudoun.legistar.com/Calendar.aspx", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)  # wait for AJAX

        print(f"API calls ({len(api_calls)}):")
        for c in api_calls[:30]:
            print(f"  {c[:150]}")

        # Also dump page content
        content = await page.content()
        print(f"\nPage content length: {len(content)}")
        # Look for any grid or calendar data
        if "GridView" in content or "rgMaster" in content or "CalendarDetail" in content:
            print("Found grid/calendar elements in HTML")
        else:
            print("No grid elements found — data probably loads via AJAX")

        # Take a screenshot
        await page.screenshot(path=r"C:\Users\sriva\VtB\scripts\loudoun_debug.png")
        print("Screenshot saved to scripts/loudoun_debug.png")

        await browser.close()


async def debug_lcps_boarddocs():
    print("\n=== LCPS BOARDDOCS — trying URL variants ===")

    urls = [
        "https://go.boarddocs.com/va/lcps/Board.nsf/Public",
        "https://go.boarddocs.com/va/lcps/Board.nsf",
        "https://go.boarddocs.com/va/lcps/Board.nsf/vpublic?open",
        "https://go.boarddocs.com/va/lcps/Board.nsf/Public?open",
    ]

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        for url in urls:
            try:
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                status = resp.status if resp else "no response"
                title = await page.title()
                body = (await page.inner_text("body"))[:200].replace("\n", " ")
                print(f"  {url}")
                print(f"    status={status} title={title!r}")
                print(f"    body={body!r}")
                await context.close()
            except Exception as e:
                print(f"  {url} -> ERROR: {e}")

        await browser.close()


async def main():
    await debug_loudoun_network()
    await debug_lcps_boarddocs()


asyncio.run(main())
