"""Gemma 4 client — the 3 prompts that power the entire app.

All prompts return only valid JSON. Retry logic handles malformed output
up to GEMMA_MAX_RETRIES times before raising GemmaError.
"""
import json
import logging
import re
import time
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

CATEGORY_SLUGS = [
    "schools-education",
    "school-construction",
    "budget-finance",
    "transportation",
    "zoning-land-use",
    "public-safety",
    "policy-governance",
    "equity-inclusion",
    "technology",
    "community-parks",
    "personnel",
    "general",
]


class GemmaError(Exception):
    pass


def _clean_json(raw: str) -> str:
    """Strip markdown code fences if Gemma ignores the no-fence instruction."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def _call_ollama(prompt: str) -> str:
    """Synchronous Ollama call — runs in the pipeline worker process (not FastAPI)."""
    url = f"{settings.ollama_base_url}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    with httpx.Client(timeout=settings.ollama_timeout) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        return response.json()["response"]


def _call_with_retry(prompt: str) -> Any:
    """Call Ollama and parse JSON, retrying on malformed output."""
    last_error: Exception | None = None
    for attempt in range(1, settings.gemma_max_retries + 2):
        try:
            raw = _call_ollama(prompt)
            return json.loads(_clean_json(raw))
        except (json.JSONDecodeError, KeyError) as exc:
            last_error = exc
            logger.warning("Gemma attempt %d failed: %s", attempt, exc)
            time.sleep(1)
    raise GemmaError(f"Gemma returned malformed JSON after {settings.gemma_max_retries + 1} attempts: {last_error}")


# ---------------------------------------------------------------------------
# Prompt 1 — Content rewrite (runs once per agenda item chunk)
# ---------------------------------------------------------------------------
PROMPT_1_TEMPLATE = """You are a civic information assistant. Read this official government document section and rewrite it in plain English for a general adult audience.

DOCUMENT SECTION:
{chunk}

Return ONLY valid JSON with exactly these fields. No markdown, no backticks, no preamble:
{{
  "title": "plain English topic title, max 10 words",
  "summary": "2-4 sentences for a general adult audience with no jargon",
  "decisions": ["exact decision or vote in plain language", "..."],
  "action_items": ["next step or follow-up action", "..."],
  "key_figures": {{
    "amounts": ["dollar amounts mentioned"],
    "vote_tallies": ["vote results like '5-2 approved'"],
    "dates": ["specific dates mentioned"],
    "schools": ["specific school names mentioned"]
  }}
}}"""


def analyze_chunk(chunk: str) -> dict:
    """Prompt 1: rewrite one agenda item chunk in plain English."""
    prompt = PROMPT_1_TEMPLATE.format(chunk=chunk.strip())
    result = _call_with_retry(prompt)
    logger.debug("Prompt 1 result keys: %s", list(result.keys()))
    return result


# ---------------------------------------------------------------------------
# Prompt 2 — Section + tag assignment (runs on the rewritten summary)
# ---------------------------------------------------------------------------
PROMPT_2_TEMPLATE = """You are a content classifier for a civic information website. Read this plain-English summary of a government agenda item and classify it.

SUMMARY:
{summary}

The 12 valid primary_category values are:
{categories}

Return ONLY valid JSON with exactly these fields. No markdown, no backticks, no preamble:
{{
  "primary_category": "one slug from the list above",
  "secondary_tags": ["specific sub-topic tags like 'bus-routes' or 'capital-budget'"],
  "urgency": "routine OR notable OR significant",
  "fiscal_impact": true or false,
  "affects_schools": ["specific school names if mentioned, else empty array"]
}}"""


def classify_item(summary: str) -> dict:
    """Prompt 2: classify a rewritten summary into website category + tags."""
    prompt = PROMPT_2_TEMPLATE.format(
        summary=summary.strip(),
        categories="\n".join(f"- {s}" for s in CATEGORY_SLUGS),
    )
    result = _call_with_retry(prompt)
    # Enforce valid category slug
    if result.get("primary_category") not in CATEGORY_SLUGS:
        logger.warning("Invalid category '%s', defaulting to 'general'", result.get("primary_category"))
        result["primary_category"] = "general"
    logger.debug("Prompt 2 result: %s", result)
    return result


# ---------------------------------------------------------------------------
# Prompt 3 — Full meeting overview (runs once per document after all chunks)
# ---------------------------------------------------------------------------
PROMPT_3_TEMPLATE = """You are a civic information assistant. Read these plain-English summaries of all agenda items from one government board meeting and write a brief meeting overview.

ALL AGENDA ITEMS:
{summaries}

Return ONLY valid JSON with exactly these fields. No markdown, no backticks, no preamble:
{{
  "meeting_overview": "3-5 sentence overview of the entire meeting for a general audience",
  "top_decisions": ["the 3 most significant decisions made"],
  "fiscal_total": "total spending approved in plain language, or null if not calculable",
  "next_meeting_notes": "any follow-up items or next steps mentioned, or null"
}}"""


def generate_meeting_overview(summaries: list[str]) -> dict:
    """Prompt 3: generate a meeting-level overview from all item summaries."""
    combined = "\n\n---\n\n".join(f"Item {i+1}: {s}" for i, s in enumerate(summaries))
    prompt = PROMPT_3_TEMPLATE.format(summaries=combined)
    result = _call_with_retry(prompt)
    logger.debug("Prompt 3 result keys: %s", list(result.keys()))
    return result
