"""Find the actual Loudoun County meetings portal."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        # Follow loudoun.gov/meetings
        page = await browser.new_page()
        all_urls = []
        page.on("request", lambda r: all_urls.append(r.url) if "meeting" in r.url.lower() or "legistar" in r.url.lower() or "agenda" in r.url.lower() else None)

        await page.goto("https://www.loudoun.gov/meetings", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        print(f"Final URL: {page.url}")
        print(f"Title: {await page.title()}")

        # Get all links on the page
        links = await page.query_selector_all("a")
        print(f"\nRelevant links on loudoun.gov/meetings:")
        for link in links:
            href = (await link.get_attribute("href") or "")
            txt = (await link.inner_text()).strip()[:60]
            if any(x in href.lower() or x in txt.lower() for x in ["board", "supervisor", "agenda", "pdf", "calendar", "meeting", "legistar", "minutes"]):
                print(f"  {txt!r} -> {href!r}")

        # Check for iframes
        frames = page.frames
        print(f"\nFrames: {len(frames)}")
        for f in frames[1:]:
            print(f"  Frame URL: {f.url}")

        print(f"\nAll meeting/legistar requests made:")
        for u in all_urls[:20]:
            print(f"  {u}")

        await page.screenshot(path=r"C:\Users\sriva\VtB\scripts\loudoun_meetings.png")
        print("\nScreenshot saved")

        # Also try the direct legistar WEBAPI with a token request first
        page2 = await browser.new_page()
        api_responses = []
        async def capture_api(resp):
            url = resp.url
            if "legistar" in url.lower() or "webapi" in url.lower():
                api_responses.append(f"{resp.status} {url[:120]}")
        page2.on("response", capture_api)
        await page2.goto("https://loudoun.legistar.com", wait_until="networkidle")
        await page2.wait_for_timeout(3000)
        print(f"\nLegistar main page responses:")
        for r in api_responses[:15]:
            print(f"  {r}")
        main_content = (await page2.inner_text("body"))[:500].replace("\n", " ").strip()
        print(f"\nLegistar body: {main_content!r}")

        await browser.close()


asyncio.run(main())
