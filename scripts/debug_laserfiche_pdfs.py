"""Drill into Laserfiche year folders to find meeting agenda PDFs."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")
from playwright.async_api import async_playwright
import re


# Year folder IDs from the index page
YEAR_FOLDERS = {
    2020: "384791",
    2021: "466681",
    2022: "559786",
    2023: "573863",
    2024: "584995",
    2025: "1947831",
    2026: "1966224",
}

LF_BASE = "https://lfportal.loudoun.gov/LFPortalinternet"


async def get_folder_contents(page, folder_id: str) -> list[dict]:
    """Get all entries in a Laserfiche folder."""
    url = f"{LF_BASE}/0/fol/{folder_id}/Row1.aspx"
    resp = await page.goto(url, wait_until="networkidle", timeout=20000)
    await page.wait_for_timeout(1000)

    entries = []
    links = await page.query_selector_all("a")
    for link in links:
        href = (await link.get_attribute("href") or "")
        txt = (await link.inner_text()).strip()
        if "/fol/" in href and txt and txt not in ("My WebLink", "Help", "About", "Sign Out", "Search"):
            fid = re.search(r"/fol/(\d+)/", href)
            entries.append({"name": txt, "type": "folder", "href": href, "id": fid.group(1) if fid else ""})
        elif "/doc/" in href and txt:
            entries.append({"name": txt, "type": "doc", "href": href})
        elif href.lower().endswith(".pdf") or ("pdf" in href.lower() and txt):
            entries.append({"name": txt, "type": "pdf", "href": href})
    return entries


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        for year in [2026, 2025, 2024]:
            folder_id = YEAR_FOLDERS[year]
            print(f"\n=== {year} (folder {folder_id}) ===")

            entries = await get_folder_contents(page, folder_id)
            print(f"  Found {len(entries)} entries:")
            for e in entries[:20]:
                print(f"  [{e['type']}] {e['name']!r} -> {e['href'][:100]!r}")

            # If these are subfolders (per meeting), pick first 3 and dig in
            subfolders = [e for e in entries if e["type"] == "folder"]
            if subfolders:
                print(f"\n  Drilling into first 3 meeting folders:")
                for sf in subfolders[:3]:
                    print(f"\n    Folder: {sf['name']!r}")
                    sub_entries = await get_folder_contents(page, sf["id"])
                    for se in sub_entries[:10]:
                        full = se["href"] if se["href"].startswith("http") else f"{LF_BASE}{se['href']}"
                        print(f"      [{se['type']}] {se['name']!r} -> {full[:120]!r}")

        await browser.close()


asyncio.run(main())
