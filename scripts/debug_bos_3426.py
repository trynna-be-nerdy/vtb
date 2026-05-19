"""Scrape BOS meetings from the correct Loudoun URL."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        urls = [
            "https://www.loudoun.gov/3426/Board-of-Supervisors-Meetings",
            "https://www.loudoun.gov/3426/Board-of-Supervisors-Meetings-Packets",
        ]

        for url in urls:
            page = await browser.new_page()
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(3000)
                status = resp.status if resp else "?"
                title = await page.title()
                print(f"\n{url}")
                print(f"  status={status}  title={title!r}")

                # Get all links
                links = await page.query_selector_all("a")
                print(f"  Total links: {len(links)}")
                for link in links:
                    href = (await link.get_attribute("href") or "")
                    txt = (await link.inner_text()).strip()[:80]
                    if any(x in href.lower() or x in txt.lower() for x in [".pdf", "packet", "agenda", "2026", "2025", "2024", "meeting", "minute"]):
                        full = href if href.startswith("http") else f"https://www.loudoun.gov{href}"
                        print(f"    {txt!r} -> {full[:100]!r}")

                # Body preview
                body = (await page.inner_text("body"))[:800].replace("\n", "  ").strip()
                print(f"  Body: {body!r}")

                # Screenshot
                name = url.split("/")[-1][:20]
                await page.screenshot(path=f"C:\\Users\\sriva\\VtB\\scripts\\{name}.png")

            except Exception as e:
                print(f"{url} -> ERROR: {e}")
            finally:
                await page.close()

        await browser.close()


asyncio.run(main())
