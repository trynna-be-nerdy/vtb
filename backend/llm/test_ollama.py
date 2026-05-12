"""
Integration test — processes a real LCPS agenda item chunk through all 3 Gemma 4 prompts.
Run: python -m backend.llm.test_ollama
Requires Ollama running locally with gemma4:4b pulled.
"""

import asyncio
import sys

from .ollama_client import rewrite_content, classify_content, generate_meeting_overview

SAMPLE_CHUNK = """\
AGENDA ITEM 7.04 — APPROVAL OF BUDGET TRANSFER FOR FACILITIES MAINTENANCE

The Superintendent recommends approval of a budget transfer in the amount of $425,000
from the General Fund Reserve to the Facilities Maintenance account to address emergency
HVAC repairs at Rock Ridge High School and Briar Woods High School.

Background: The HVAC systems at both facilities experienced significant failures during
the current school year. Rock Ridge High School requires replacement of three primary
air handling units at an estimated cost of $265,000. Briar Woods High School requires
replacement of two units at an estimated cost of $160,000. These repairs are necessary
to maintain appropriate learning environments for approximately 3,800 students.

The Board voted 7-2 to approve the budget transfer, with Board Members Harrison and
Barts voting in opposition.

Next steps: The Facilities Management office will issue purchase orders within 30 days.
Construction is expected to begin January 15, 2026, with completion by March 1, 2026.
"""

SECOND_SUMMARY = (
    "The board discussed proposed changes to the 2026-2027 academic calendar, "
    "including adding two additional professional development days and adjusting "
    "winter break. No vote was taken; feedback from staff and parents will be "
    "collected over the next 30 days before a final decision."
)


async def run_tests() -> bool:
    passed = True

    print("=" * 60)
    print("View the Board — Gemma 4 Integration Test")
    print(f"Model: {__import__('os').getenv('OLLAMA_MODEL', 'gemma4:26b')}")
    print("=" * 60)

    # --- Prompt 1 ---
    print("\n[1/3] Prompt 1: Content Rewrite")
    try:
        result1 = await rewrite_content(SAMPLE_CHUNK)
        print(f"  title        : {result1.title}")
        print(f"  summary      : {result1.summary[:120]}...")
        print(f"  decisions    : {result1.decisions}")
        print(f"  action_items : {result1.action_items}")
        print(f"  key_figures  : {result1.key_figures.model_dump()}")
        print("  PASS")
    except Exception as exc:
        print(f"  FAIL — {exc}")
        passed = False
        return passed  # can't continue without summary

    # --- Prompt 2 ---
    print("\n[2/3] Prompt 2: Classification")
    try:
        result2 = await classify_content(result1.summary)
        print(f"  primary_category : {result2.primary_category}")
        print(f"  secondary_tags   : {result2.secondary_tags}")
        print(f"  urgency          : {result2.urgency}")
        print(f"  fiscal_impact    : {result2.fiscal_impact}")
        print(f"  affects_schools  : {result2.affects_schools}")
        print("  PASS")
    except Exception as exc:
        print(f"  FAIL — {exc}")
        passed = False

    # --- Prompt 3 ---
    print("\n[3/3] Prompt 3: Meeting Overview")
    try:
        result3 = await generate_meeting_overview([result1.summary, SECOND_SUMMARY])
        print(f"  meeting_overview    : {result3.meeting_overview[:120]}...")
        print(f"  top_decisions       : {result3.top_decisions}")
        print(f"  fiscal_total        : {result3.fiscal_total}")
        print(f"  next_meeting_notes  : {result3.next_meeting_notes}")
        print("  PASS")
    except Exception as exc:
        print(f"  FAIL — {exc}")
        passed = False

    print("\n" + "=" * 60)
    print("Result:", "ALL TESTS PASSED" if passed else "SOME TESTS FAILED")
    print("=" * 60)
    return passed


if __name__ == "__main__":
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)
