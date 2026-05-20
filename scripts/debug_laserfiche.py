"""Explore Loudoun Laserfiche portal for meeting PDFs."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def main():
    base = "https://lfportal.loudoun.gov/LFPortalinternet"

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        # Direct Laserfiche folder
        url = f"{base}/0/fol/98907/Row1.aspx"
        print(f"Loading: {url}")

        resp = await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        print(f"Status: {resp.status if resp else '?'}")
        print(f"Title: {await page.title()}")

        # Get all links
        links = await page.query_selector_all("a")
        print(f"Links: {len(links)}")
        for link in links[:40]:
            href = (await link.get_attribute("href") or "")
            txt = (await link.inner_text()).strip()[:80]
            if txt:
                full = href if href.startswith("http") else f"{base}{href}" if href else ""
                print(f"  {txt!r} -> {full[:120]!r}")

        # Screenshot
        await page.screenshot(path=r"C:\Users\sriva\VtB\scripts\laserfiche.png", full_page=True)
        print("\nScreenshot saved")

        # Body preview
        body = (await page.inner_text("body"))[:1500].replace("\n", "  ").strip()
        print(f"\nBody: {body!r}")

        # Try browsing to see folder contents
        # Laserfiche typically has folders per year
        test_paths = [
            f"{base}/0/fol/98907/Row1.aspx",
            f"{base}/Browse.aspx?id=98907",
            f"{base}/DocView.aspx?id=98907",
        ]
        for path in test_paths[1:]:
            try:
                p2 = await browser.new_page()
                r2 = await p2.goto(path, wait_until="domcontentloaded", timeout=15000)
                txt = (await p2.inner_text("body"))[:400].replace("\n"," ").strip()
                print(f"\n{path}")
                print(f"  status={r2.status if r2 else '?'} body={txt!r}")
                await p2.close()
            except Exception as e:
                print(f"\n{path} -> ERROR: {e}")

        await browser.close()


asyncio.run(main())
