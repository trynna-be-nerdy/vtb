"""Find the correct Loudoun Legistar calendar URL."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        # Try URLs with different params
        test_urls = [
            "https://loudoun.legistar.com/",
            "https://loudoun.legistar.com/Calendar.aspx?Year=2026",
            "https://loudoun.legistar.com/Calendar.aspx?DepartmentId=0",
            "https://loudoun.legistar.com/Meetings.aspx",
            "https://loudoun.legistar.com/MeetingCalendar.aspx",
        ]

        for url in test_urls:
            page = await browser.new_page()
            try:
                resp = await page.goto(url, wait_until="domcontentloaded", timeout=12000)
                await page.wait_for_timeout(2000)
                status = resp.status if resp else "?"
                title = await page.title()
                body = (await page.inner_text("body"))[:200].replace("\n", " ").strip()
                links = await page.query_selector_all("a")
                print(f"{url}")
                print(f"  status={status}  title={title!r}")
                print(f"  body={body!r}")
                # Show relevant links
                for link in links[:15]:
                    href = (await link.get_attribute("href") or "")
                    txt = (await link.inner_text()).strip()[:40]
                    if any(x in href.lower() or x in txt.lower() for x in ["calendar", "meeting", "agenda", "board", "supervisor"]):
                        print(f"    LINK: {txt!r} -> {href!r}")
            except Exception as e:
                print(f"{url} -> ERROR: {e}")
            finally:
                await page.close()

        await browser.close()


asyncio.run(main())
