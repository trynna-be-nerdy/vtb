"""Find actual BOS meeting packet PDFs."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright
import re


async def find_pdfs(page, base="https://www.loudoun.gov"):
    """Return all PDF links on current page."""
    links = await page.query_selector_all("a")
    pdfs = []
    for link in links:
        href = (await link.get_attribute("href") or "")
        txt = (await link.inner_text()).strip()
        if ".pdf" in href.lower():
            full = href if href.startswith("http") else f"{base}{href}"
            pdfs.append((txt[:60], full))
    return pdfs


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        # Try the direct agenda packets URL
        urls_to_try = [
            "https://www.loudoun.gov/4829",
            "https://www.loudoun.gov/4829/Board-of-Supervisors-Meeting-Documents",
            "https://www.loudoun.gov/archive.aspx?AMID=37",   # Common CivicPlus archive ID
            "https://www.loudoun.gov/archive.aspx?ADID=37",
        ]

        for url in urls_to_try:
            page = await browser.new_page()
            try:
                resp = await page.goto(url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(1500)
                status = resp.status if resp else "?"
                title = await page.title()
                pdfs = await find_pdfs(page)
                print(f"\n{url}")
                print(f"  status={status}  title={title!r}")
                print(f"  PDFs: {len(pdfs)}")
                for txt, href in pdfs[:8]:
                    print(f"    {txt!r} -> {href!r}")

                # Also look for sub-links
                links = await page.query_selector_all("a")
                print(f"  Links with 'packet' or 'agenda' or '2026' or '2025':")
                for link in links:
                    href = (await link.get_attribute("href") or "")
                    txt = (await link.inner_text()).strip()
                    if any(x in txt.lower() or x in href.lower() for x in ["packet", "agenda", "2026", "2025", "business meeting"]):
                        full = href if href.startswith("http") else f"https://www.loudoun.gov{href}"
                        print(f"    {txt[:50]!r} -> {full!r}")
            except Exception as e:
                print(f"{url} -> ERROR: {e}")
            finally:
                await page.close()

        # Try LCPS - look for their new meeting portal
        print("\n\n=== LCPS Meeting Portal Search ===")
        lcps_urls = [
            "https://www.lcps.org/Page/71",   # common board page IDs
            "https://www.lcps.org/Page/1",
            "https://www.lcps.org/boardofed",
            "https://www.lcps.org/domain/86",
        ]
        for url in lcps_urls:
            page = await browser.new_page()
            try:
                resp = await page.goto(url, wait_until="networkidle", timeout=15000)
                await page.wait_for_timeout(2000)
                status = resp.status if resp else "?"
                title = await page.title()
                body = (await page.inner_text("body"))[:300].replace("\n"," ").strip()
                print(f"\n{url}")
                print(f"  status={status}  title={title!r}")
                print(f"  body={body!r}")
                pdfs = await find_pdfs(page, "https://www.lcps.org")
                print(f"  PDFs: {len(pdfs)}")
                for txt, href in pdfs[:5]:
                    print(f"    {txt!r} -> {href!r}")
            except Exception as e:
                print(f"{url} -> ERROR: {e}")
            finally:
                await page.close()

        await browser.close()


asyncio.run(main())
