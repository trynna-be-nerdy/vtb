"""
Gemma 4 integration via Ollama.
Provides three async prompt functions for the View the Board pipeline.
"""

import json
import os
from typing import TypeVar, Type

import httpx
from pydantic import BaseModel, ValidationError

from .models import ContentRewriteResult, ClassificationResult, MeetingOverviewResult

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "gemma4:26b")

# Connect timeout stays short; read timeout is None (no limit) because local
# Ollama takes as long as it needs — especially the 26B model on CPU layers.
_CONNECT_TIMEOUT = float(os.getenv("OLLAMA_CONNECT_TIMEOUT", "10"))
_READ_TIMEOUT: float | None = None
if _rt := os.getenv("OLLAMA_READ_TIMEOUT"):
    _READ_TIMEOUT = float(_rt)
_TIMEOUT = httpx.Timeout(connect=_CONNECT_TIMEOUT, read=_READ_TIMEOUT, write=30, pool=5)

MAX_RETRIES = 2

T = TypeVar("T", bound=BaseModel)

_RETRY_SUFFIX = (
    "\n\nCRITICAL: Your previous response was not valid JSON or had missing fields. "
    "Return ONLY a raw JSON object — no markdown fences, no backticks, no explanatory text, "
    "nothing before or after the opening and closing braces."
)

_PROMPT_1 = """\
You are a plain-English rewriter for government meeting documents.
Analyze the official government meeting text below and return ONLY a valid JSON object.
No markdown, no backticks, no explanation before or after the JSON.

Required JSON structure (all fields mandatory):
{{
  "title": "<topic in plain English, maximum 10 words>",
  "summary": "<2-4 sentences for a general adult audience, no jargon>",
  "decisions": ["<exact decision or vote in plain language>"],
  "action_items": ["<next step or follow-up action>"],
  "key_figures": {{
    "amounts": ["<dollar amounts mentioned>"],
    "vote_tallies": ["<vote results like '5-2 approved'>"],
    "dates": ["<specific dates mentioned>"],
    "schools": ["<specific school names mentioned>"]
  }}
}}

Government meeting text:
{chunk}"""

_PROMPT_2 = """\
You are a classifier for local government meeting content.
Analyze the meeting summary below and return ONLY a valid JSON object.
No markdown, no backticks, no text before or after the JSON.

The primary_category MUST be exactly one of these 12 slugs:
schools-education | school-construction | budget-finance | transportation |
zoning-land-use | public-safety | policy-governance | equity-inclusion |
technology | community-parks | personnel | general

Required JSON structure (all fields mandatory):
{{
  "primary_category": "<one slug from the list above>",
  "secondary_tags": ["<specific sub-topic tag>"],
  "urgency": "<routine OR notable OR significant>",
  "fiscal_impact": <true or false>,
  "affects_schools": ["<school name if mentioned — empty array if none>"]
}}

Meeting summary:
{summary}"""

_PROMPT_3 = """\
You are a summarizer for local government meetings.
Review all agenda item summaries below from one meeting and return ONLY a valid JSON object.
No markdown, no backticks, no text before or after the JSON.

Required JSON structure (all fields mandatory):
{{
  "meeting_overview": "<3-5 sentence overview of the entire meeting for a general audience>",
  "top_decisions": ["<1st most significant decision>", "<2nd>", "<3rd>"],
  "fiscal_total": "<total spending approved as a string like '$2.3M', or null if none>",
  "next_meeting_notes": "<scheduled follow-up items or next meeting info, or null if none>"
}}

Agenda item summaries:
{summaries}"""


async def _call_ollama(prompt: str, response_schema: dict | None = None) -> str:
    format_param: dict | str = response_schema if response_schema else "json"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "format": format_param,
            },
        )
        resp.raise_for_status()
        return resp.json()["response"]


async def _parse_with_retry(
    prompt: str,
    model_class: Type[T],
    schema: dict | None = None,
) -> T:
    current_prompt = prompt
    last_error: Exception | None = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            raw = await _call_ollama(current_prompt, schema)
            data = json.loads(raw)
            return model_class(**data)
        except (json.JSONDecodeError, ValidationError, KeyError, TypeError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                current_prompt = prompt + _RETRY_SUFFIX

    raise ValueError(
        f"Gemma 4 failed to return valid {model_class.__name__} "
        f"after {MAX_RETRIES + 1} attempts. Last error: {last_error}"
    )


async def rewrite_content(chunk: str) -> ContentRewriteResult:
    """Prompt 1 — rewrite one agenda item chunk into plain English."""
    prompt = _PROMPT_1.format(chunk=chunk)
    schema = ContentRewriteResult.model_json_schema()
    return await _parse_with_retry(prompt, ContentRewriteResult, schema)


async def classify_content(summary: str) -> ClassificationResult:
    """Prompt 2 — assign category, urgency, and fiscal flags to a rewritten summary."""
    prompt = _PROMPT_2.format(summary=summary)
    schema = ClassificationResult.model_json_schema()
    return await _parse_with_retry(prompt, ClassificationResult, schema)


async def generate_meeting_overview(summaries: list[str]) -> MeetingOverviewResult:
    """Prompt 3 — synthesise all item summaries into a meeting-level overview."""
    combined = "\n\n---\n\n".join(summaries)
    prompt = _PROMPT_3.format(summaries=combined)
    schema = MeetingOverviewResult.model_json_schema()
    return await _parse_with_retry(prompt, MeetingOverviewResult, schema)
