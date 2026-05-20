"""Scroll down BOS meetings page and find iframes/embedded content."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        await page.goto("https://www.loudoun.gov/3426/Board-of-Supervisors-Meetings-Packets", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(3000)

        # Scroll down to trigger lazy loading
        await page.evaluate("window.scrollTo(0, 2000)")
        await page.wait_for_timeout(2000)
        await page.evaluate("window.scrollTo(0, 4000)")
        await page.wait_for_timeout(2000)

        # Check for iframes
        frames = page.frames
        print(f"Frames ({len(frames)}):")
        for f in frames:
            if f.url and "loudoun.gov" not in f.url and f.url != "about:blank":
                print(f"  {f.url[:150]}")
                # Try to get content from frame
                try:
                    frame_links = await f.query_selector_all("a")
                    for link in frame_links[:10]:
                        href = await link.get_attribute("href") or ""
                        txt = (await link.inner_text()).strip()[:60]
                        if txt or href:
                            print(f"    LINK: {txt!r} -> {href!r}")
                except Exception as e:
                    print(f"    (frame error: {e})")

        # Full page screenshot after scroll
        await page.screenshot(path=r"C:\Users\sriva\VtB\scripts\bos_scroll.png", full_page=True)
        print("Full page screenshot saved")

        # Get all network responses that happened
        print("\nAll text content sections:")
        sections = await page.query_selector_all(".field-items, .cms-content, .content-area, #cms-content, main, article, .main-content")
        for s in sections:
            txt = (await s.inner_text()).strip()[:500].replace("\n", "  ")
            if txt:
                print(f"  Section: {txt!r}")

        # Try to find the iframe specifically
        iframes = await page.query_selector_all("iframe")
        print(f"\niFrames: {len(iframes)}")
        for iframe in iframes:
            src = await iframe.get_attribute("src") or ""
            print(f"  src={src!r}")

        await browser.close()


asyncio.run(main())
