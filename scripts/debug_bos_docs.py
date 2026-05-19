"""Find BOS meeting document PDFs on loudoun.gov."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright
import re


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        # The actual BOS meeting documents page
        await page.goto("https://www.loudoun.gov/4829/Board-of-Supervisors-Meeting-Documents", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        print(f"Title: {await page.title()}")
        body = (await page.inner_text("body"))[:2000].replace("\n", "  ").strip()
        print(f"Body preview:\n{body}")

        print("\n-- All PDF links --")
        links = await page.query_selector_all("a")
        for link in links:
            href = (await link.get_attribute("href") or "")
            txt = (await link.inner_text()).strip()[:80]
            if ".pdf" in href.lower() or "agenda" in href.lower() or "agenda" in txt.lower() or "minutes" in txt.lower():
                full = href if href.startswith("http") else f"https://www.loudoun.gov{href}"
                print(f"  {txt!r}  ->  {full!r}")

        print("\n-- Page structure --")
        headings = await page.query_selector_all("h1, h2, h3, h4")
        for h in headings:
            print(f"  H: {(await h.inner_text()).strip()!r}")

        # Screenshot
        await page.screenshot(path=r"C:\Users\sriva\VtB\scripts\bos_docs.png")

        await browser.close()


asyncio.run(main())
