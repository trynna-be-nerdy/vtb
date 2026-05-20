"""Intercept BoardDocs network requests to find the meetings API."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright
import json


async def main():
    api_calls = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124"
        )
        page = await context.new_page()

        # Intercept responses
        async def on_response(resp):
            url = resp.url
            if "boarddocs" in url.lower() and resp.status == 200:
                content_type = resp.headers.get("content-type", "")
                if "json" in content_type or "text" in content_type:
                    try:
                        body = await resp.text()
                        if len(body) > 50 and ("meeting" in body.lower() or "date" in body.lower()):
                            api_calls.append({"url": url, "body": body[:500]})
                    except Exception:
                        pass

        page.on("response", on_response)

        print("Loading BoardDocs...")
        await page.goto("https://go.boarddocs.com/vsba/loudoun/Board.nsf/Public", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        print(f"Title: {await page.title()}")
        print(f"API calls so far: {len(api_calls)}")

        # Click MEETINGS tab
        print("\nClicking MEETINGS tab...")
        try:
            await page.click("text=MEETINGS", timeout=5000)
        except Exception:
            try:
                await page.click("[href*='meetings'], [data-tab*='meeting'], a:has-text('Meetings')", timeout=5000)
            except Exception as e:
                print(f"  Click failed: {e}")

        await page.wait_for_timeout(4000)
        print(f"API calls after click: {len(api_calls)}")

        # Print all API calls
        for call in api_calls:
            print(f"\n  URL: {call['url']}")
            print(f"  Body: {call['body'][:300]}")

        # Also check page content now
        body_text = (await page.inner_text("body"))[:1500].replace("\n", "  ")
        print(f"\nPage body after MEETINGS click:\n{body_text!r}")

        # Take screenshot
        await page.screenshot(path=r"C:\Users\sriva\VtB\scripts\boarddocs_meetings.png")
        print("\nScreenshot saved")

        # Look for any meeting-looking elements
        links = await page.query_selector_all("a, button, li, tr")
        print(f"\nElements containing dates ({len(links)} total):")
        import re
        for el in links:
            txt = (await el.inner_text()).strip()
            if re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\b.*\d{4}', txt):
                print(f"  {el.element.__class__.__name__ if hasattr(el, 'element') else 'el'}: {txt[:80]!r}")

        await browser.close()


asyncio.run(main())
