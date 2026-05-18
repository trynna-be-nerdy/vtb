"""
LCPS School Board scraper.

Uses Playwright to load the LCPS Board of Education page and BoardDocs
because both sites use Cloudflare / JS challenges that block plain HTTP.
"""

import logging
import re
from datetime import date, datetime

from playwright.async_api import async_playwright

from .base import BaseScraper, DocumentInfo

logger = logging.getLogger(__name__)

_LCPS_BOARD_URL  = "https://www.lcps.org/boardofed"
_BOARDDOCS_URL   = "https://go.boarddocs.com/va/lcps/Board.nsf/Public"


def _parse_date(raw: str) -> date | None:
    for fmt in ("%B %d, %Y", "%m/%d/%Y", "%Y-%m-%d", "%b %d, %Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except ValueError:
            continue
    return None


class LCPSScraper(BaseScraper):
    """Discover LCPS board meeting agendas via Playwright."""

    async def discover_documents(self) -> list[DocumentInfo]:
        docs: list[DocumentInfo] = []
        try:
            docs = await self._scrape_boarddocs()
        except Exception:
            logger.exception("LCPSScraper BoardDocs scrape failed, trying lcps.org")
            try:
                docs = await self._scrape_lcps_org()
            except Exception:
                logger.exception("LCPSScraper lcps.org fallback also failed")
        logger.info("LCPSScraper discovered %d documents", len(docs))
        return docs

    async def _scrape_boarddocs(self) -> list[DocumentInfo]:
        """Scrape BoardDocs public portal for LCPS meeting agendas."""
        docs: list[DocumentInfo] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124"
            )
            page = await context.new_page()
            page.set_default_timeout(30_000)

            await page.goto(_BOARDDOCS_URL, wait_until="networkidle")

            # BoardDocs loads meeting list via JS — wait for the meeting container
            try:
                await page.wait_for_selector(".meeting-list, #meetings, .meetings-container, li.meeting", timeout=15_000)
            except Exception:
                logger.warning("BoardDocs meeting list not found — page may have changed")

            # Extract meeting links
            meeting_links = await page.query_selector_all("a[href*='MeetingDetail'], a[href*='meeting'], a[href*='Meeting']")

            for link in meeting_links:
                try:
                    href = await link.get_attribute("href") or ""
                    text = (await link.inner_text()).strip()

                    # Skip navigation and non-meeting links
                    if len(text) < 6 or "BoardDocs" in text:
                        continue

                    # Try to find a date in the link text
                    date_match = re.search(r'(\w+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})', text)
                    if not date_match:
                        continue

                    meeting_date = _parse_date(date_match.group(1))
                    if not meeting_date:
                        continue

                    full_url = href if href.startswith("http") else f"https://go.boarddocs.com{href}"

                    docs.append(DocumentInfo(
                        url=full_url,
                        pdf_url=full_url,
                        title=f"LCPS School Board Meeting – {meeting_date.strftime('%B %-d, %Y')}",
                        meeting_date=meeting_date,
                        board_type="lcps-school-board",
                    ))
                except Exception as exc:
                    logger.debug("Skipping BoardDocs link: %s", exc)

            await browser.close()

        return docs

    async def _scrape_lcps_org(self) -> list[DocumentInfo]:
        """Fallback: scrape lcps.org/boardofed for meeting agenda PDF links."""
        docs: list[DocumentInfo] = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()
            page.set_default_timeout(30_000)

            await page.goto(_LCPS_BOARD_URL, wait_until="networkidle")

            # Look for PDF links with meeting-related text
            links = await page.query_selector_all("a[href$='.pdf'], a[href*='agenda'], a[href*='Agenda']")

            for link in links:
                try:
                    href = await link.get_attribute("href") or ""
                    text = (await link.inner_text()).strip()
                    if not href:
                        continue

                    # Find date near the link
                    parent_text = await (await link.evaluate_handle("el => el.closest('li, tr, div, p') || el.parentElement")).evaluate("el => el.innerText")
                    date_match = re.search(r'(\w+ \d{1,2},? \d{4}|\d{1,2}/\d{1,2}/\d{4})', parent_text)
                    if not date_match:
                        continue

                    meeting_date = _parse_date(date_match.group(1))
                    if not meeting_date:
                        continue

                    full_url = href if href.startswith("http") else f"https://www.lcps.org{href}"

                    docs.append(DocumentInfo(
                        url=f"https://www.lcps.org/boardofed",
                        pdf_url=full_url,
                        title=f"LCPS School Board Meeting – {meeting_date.strftime('%B %-d, %Y')}",
                        meeting_date=meeting_date,
                        board_type="lcps-school-board",
                    ))
                except Exception as exc:
                    logger.debug("Skipping lcps.org link: %s", exc)

            await browser.close()

        return docs
