"""
LCPS School Board scraper.

Uses Playwright to navigate the LCPS BoardDocs portal at:
  https://go.boarddocs.com/vsba/loudoun/Board.nsf/Public

BoardDocs is a JS-heavy SPA. We click the MEETINGS tab to get the
meeting list, then extract agenda PDF links from each meeting.
"""

import logging
import re
from datetime import date, datetime

from playwright.async_api import async_playwright

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

_BOARDDOCS_URL = "https://go.boarddocs.com/vsba/loudoun/Board.nsf/Public"
_BOARD_TYPE    = "lcps-school-board"


def _parse_date(raw: str) -> date | None:
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%m/%d/%Y", "%Y-%m-%d",
                "%B %d %Y", "%A, %B %d, %Y"):
        try:
            return datetime.strptime(raw.strip().rstrip(","), fmt).date()
        except ValueError:
            continue
    # Try removing ordinal suffixes (1st, 2nd, 3rd, 4th)
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", raw.strip())
    for fmt in ("%B %d, %Y", "%B %d %Y"):
        try:
            return datetime.strptime(cleaned.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _day_str(d: date) -> str:
    return f"{d.strftime('%B')} {d.day}, {d.year}"


class LCPSScraper(BaseScraper):
    """Discover LCPS school board meeting agendas via BoardDocs."""

    async def discover_documents(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []
        try:
            docs = await self._scrape_boarddocs()
        except Exception:
            logger.exception("LCPSScraper BoardDocs scrape failed")
        logger.info("LCPSScraper discovered %d documents", len(docs))
        return docs

    async def _scrape_boarddocs(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            page.set_default_timeout(30_000)

            await page.goto(_BOARDDOCS_URL, wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Click the MEETINGS tab
            try:
                meetings_tab = page.locator("text=MEETINGS").first
                await meetings_tab.click()
                await page.wait_for_timeout(3000)
                logger.info("Clicked MEETINGS tab")
            except Exception:
                logger.warning("Could not click MEETINGS tab — trying direct nav")
                await page.goto(_BOARDDOCS_URL + "#meetings", wait_until="networkidle")
                await page.wait_for_timeout(3000)

            # Extract meeting rows — BoardDocs renders a list of meetings
            # Try common selectors
            meeting_rows = await page.query_selector_all(
                "li.meeting-item, div.meeting-item, tr.meeting-row, "
                ".meetings-list li, #meetings-list li, "
                "[class*='meeting'] a, .meeting a"
            )

            if not meeting_rows:
                # Fallback: get all links that look like meeting entries
                all_links = await page.query_selector_all("a")
                for link in all_links:
                    href = await link.get_attribute("href") or ""
                    txt = (await link.inner_text()).strip()
                    if len(txt) > 8 and re.search(r"\d{4}", txt):
                        date_val = _parse_date(txt)
                        if date_val:
                            meeting_rows.append(link)

            logger.info("BoardDocs meeting rows found: %d", len(meeting_rows))

            # Capture XHR responses for agenda data
            pdf_urls_seen: set[str] = set()

            for row in meeting_rows[:60]:  # limit to recent 60 meetings
                try:
                    txt = (await row.inner_text()).strip()
                    meeting_date = _parse_date(txt)
                    if not meeting_date:
                        continue

                    # Click the meeting to load its agenda
                    await row.click()
                    await page.wait_for_timeout(2000)

                    # Look for PDF links in the loaded content
                    pdf_links = await page.query_selector_all("a[href*='.pdf'], a[href*='pdf']")
                    pdf_url = None
                    for pl in pdf_links:
                        href = await pl.get_attribute("href") or ""
                        if ".pdf" in href.lower() and href not in pdf_urls_seen:
                            pdf_url = href if href.startswith("http") else f"https://go.boarddocs.com{href}"
                            pdf_urls_seen.add(pdf_url)
                            break

                    landing = page.url
                    docs.append(DocumentInfo(
                        url=landing,
                        pdf_url=pdf_url or landing,
                        title=f"LCPS School Board Meeting – {_day_str(meeting_date)}",
                        meeting_date=meeting_date,
                        board_type=_BOARD_TYPE,
                    ))

                    # Go back to meetings list
                    await page.go_back()
                    await page.wait_for_timeout(1500)

                except Exception as exc:
                    logger.debug("Skipping LCPS meeting row: %s", exc)
                    continue

            # If we found nothing via clicking, try the XHR API directly
            if not docs:
                docs = await self._scrape_boarddocs_api(page)

            await browser.close()

        return docs

    async def _scrape_boarddocs_api(self, page) -> list[DocumentInfo]:
        """Try BoardDocs internal API for meeting list."""
        docs = []
        try:
            # BoardDocs typically exposes a meetings JSON endpoint
            api_url = "https://go.boarddocs.com/vsba/loudoun/Board.nsf/GetMeetings?open"
            resp = await page.request.get(api_url)
            if resp.status == 200:
                data = await resp.json()
                meetings = data if isinstance(data, list) else data.get("meetings", [])
                for m in meetings[:60]:
                    raw_date = m.get("date") or m.get("startDate") or m.get("meetingDate") or ""
                    meeting_date = _parse_date(raw_date)
                    if not meeting_date:
                        continue
                    unique = m.get("unique") or m.get("id") or ""
                    pdf_url = f"https://go.boarddocs.com/vsba/loudoun/Board.nsf/{unique}" if unique else _BOARDDOCS_URL
                    docs.append(DocumentInfo(
                        url=_BOARDDOCS_URL,
                        pdf_url=pdf_url,
                        title=f"LCPS School Board Meeting – {_day_str(meeting_date)}",
                        meeting_date=meeting_date,
                        board_type=_BOARD_TYPE,
                    ))
        except Exception as exc:
            logger.debug("BoardDocs API fallback failed: %s", exc)

        return docs
