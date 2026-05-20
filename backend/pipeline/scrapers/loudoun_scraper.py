"""
Loudoun County Board of Supervisors scraper.

Uses Playwright to navigate the Loudoun County Laserfiche WebLink portal
at lfportal.loudoun.gov, which hosts all BOS meeting agenda PDFs organized
by year → meeting folder → individual documents.

Portal root: https://lfportal.loudoun.gov/LFPortalinternet/0/fol/98907/Row1.aspx
"""

import logging
import re
from datetime import date, datetime

from playwright.async_api import async_playwright, Page

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

LF_BASE   = "https://lfportal.loudoun.gov/LFPortalinternet"
LF_ROOT   = f"{LF_BASE}/0/fol/98907/Row1.aspx"

# Laserfiche folder IDs per year (discovered from portal index)
YEAR_FOLDER_IDS: dict[int, str] = {
    2020: "384791",
    2021: "466681",
    2022: "559786",
    2023: "573863",
    2024: "584995",
    2025: "1947831",
    2026: "1966224",
}

# Board type mapping from meeting folder name
_BOARD_MAP: list[tuple[str, str]] = [
    ("planning commission", "planning-commission"),
    ("planning",            "planning-commission"),
    ("advisory",            "advisory-boards"),
    ("supervisor",          "board-of-supervisors"),
    ("business meeting",    "board-of-supervisors"),
    ("public hearing",      "board-of-supervisors"),
    ("special",             "board-of-supervisors"),
    ("budget",              "board-of-supervisors"),
]


def _map_board(name: str) -> str:
    lower = name.lower()
    for fragment, slug in _BOARD_MAP:
        if fragment in lower:
            return slug
    return "board-of-supervisors"


def _parse_folder_date(folder_name: str) -> date | None:
    """Parse '05-07-26 Business Meeting' → date(2026, 5, 7)."""
    m = re.match(r"(\d{2})-(\d{2})-(\d{2})", folder_name)
    if not m:
        return None
    mon, day, yr = int(m.group(1)), int(m.group(2)), int(m.group(3))
    year = 2000 + yr
    try:
        return date(year, mon, day)
    except ValueError:
        return None


def _fix_lf_url(href: str) -> str:
    """Convert Laserfiche relative edoc path to absolute URL."""
    if href.startswith("http"):
        return href
    # href like: ../../edoc/1234567/filename.pdf
    # base page: https://lfportal.loudoun.gov/LFPortalinternet/0/fol/.../Row1.aspx
    # resolved:  https://lfportal.loudoun.gov/edoc/1234567/filename.pdf
    if "edoc/" in href:
        edoc_part = href[href.index("edoc/"):]
        return f"https://lfportal.loudoun.gov/{edoc_part}"
    if href.startswith("/"):
        return f"https://lfportal.loudoun.gov{href}"
    return f"https://lfportal.loudoun.gov/LFPortalinternet/{href}"


async def _get_folder_entries(page: Page, folder_id: str) -> list[dict]:
    """Return entries (folders and docs) from a Laserfiche folder page."""
    url = f"{LF_BASE}/0/fol/{folder_id}/Row1.aspx"
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_timeout(800)
    except Exception as exc:
        logger.warning("Failed to load LF folder %s: %s", folder_id, exc)
        return []

    entries = []
    links = await page.query_selector_all("a")
    seen = set()

    for link in links:
        href = (await link.get_attribute("href") or "").strip()
        txt  = (await link.inner_text()).strip()

        if not txt or href in seen:
            continue
        seen.add(href)

        # Skip navigation links
        if txt in ("My WebLink", "Help", "About", "Sign Out", "Search", "Name", "Laserfiche."):
            continue
        if "javascript:" in href and "__doPostBack" in href:
            # Breadcrumb navigation — skip
            continue

        if "/fol/" in href:
            fid = re.search(r"/fol/(\d+)/", href)
            if fid:
                entries.append({"name": txt, "type": "folder", "id": fid.group(1), "href": href})
        elif "edoc/" in href or href.lower().endswith(".pdf"):
            entries.append({"name": txt, "type": "pdf", "href": _fix_lf_url(href)})

    return entries


class LoudounScraper(BaseScraper):
    """Discover Loudoun County BOS meeting agenda PDFs from Laserfiche portal."""

    async def discover_documents(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []
        try:
            docs = await self._scrape_laserfiche()
        except Exception:
            logger.exception("LoudounScraper Laserfiche scrape failed")
        logger.info("LoudounScraper discovered %d documents", len(docs))
        return docs

    async def _scrape_laserfiche(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()

            # Scrape current year and previous year to catch recent meetings
            from datetime import date as _date
            current_year = _date.today().year
            years_to_scrape = [current_year, current_year - 1]

            for year in years_to_scrape:
                folder_id = YEAR_FOLDER_IDS.get(year)
                if not folder_id:
                    continue

                logger.info("Scraping Laserfiche year %d (folder %s)", year, folder_id)
                year_entries = await _get_folder_entries(page, folder_id)
                meeting_folders = [e for e in year_entries if e["type"] == "folder"]

                for mf in meeting_folders:
                    meeting_date = _parse_folder_date(mf["name"])
                    if not meeting_date:
                        continue

                    board_type = _map_board(mf["name"])
                    day_str = str(meeting_date.day)  # no zero-pad, cross-platform
                    suffix = mf["name"].split(" ", 1)[1].title() if " " in mf["name"] else mf["name"]
                    title = f"{suffix} – {meeting_date.strftime('%B')} {day_str}, {meeting_date.year}"

                    # Get PDFs inside meeting folder
                    meeting_entries = await _get_folder_entries(page, mf["id"])
                    pdfs = [e for e in meeting_entries if e["type"] == "pdf"]

                    # Prefer Agenda Summary or Agenda PDF as the main document
                    main_pdf = None
                    for priority in ["Agenda Summary", "Agenda.pdf", "Agenda"]:
                        for pdf in pdfs:
                            if priority.lower() in pdf["name"].lower():
                                main_pdf = pdf
                                break
                        if main_pdf:
                            break

                    if not main_pdf and pdfs:
                        main_pdf = pdfs[0]

                    if not main_pdf:
                        logger.debug("No PDF found in meeting folder %s", mf["name"])
                        continue

                    landing = f"{LF_BASE}/0/fol/{mf['id']}/Row1.aspx"

                    docs.append(DocumentInfo(
                        url=landing,
                        pdf_url=main_pdf["href"],
                        title=title,
                        meeting_date=meeting_date,
                        board_type=board_type,
                    ))

                    # Rate limit between meetings
                    await page.wait_for_timeout(1000)

            await browser.close()

        return docs
