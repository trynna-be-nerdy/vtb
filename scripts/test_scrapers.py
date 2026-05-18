"""Quick scraper test — prints discovered documents without running Gemma."""
import asyncio
import sys
sys.path.insert(0, r"C:\Users\sriva\VtB")

from backend.pipeline.scrapers.loudoun_scraper import LoudounScraper
from backend.pipeline.scrapers.lcps_scraper import LCPSScraper


async def main():
    print("── Loudoun County Scraper ──────────────────────")
    try:
        docs = await LoudounScraper().discover_documents()
        print(f"Found {len(docs)} documents")
        for d in docs[:5]:
            print(f"  {d.meeting_date}  {d.board_type:<30}  {d.title[:60]}")
    except Exception as e:
        print(f"ERROR: {e}")

    print()
    print("── LCPS Scraper ────────────────────────────────")
    try:
        docs = await LCPSScraper().discover_documents()
        print(f"Found {len(docs)} documents")
        for d in docs[:5]:
            print(f"  {d.meeting_date}  {d.board_type:<30}  {d.title[:60]}")
    except Exception as e:
        print(f"ERROR: {e}")


asyncio.run(main())
