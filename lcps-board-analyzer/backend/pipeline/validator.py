"""10-check quality gate — runs before any DB write.

Raises ValidationError with a descriptive message if any check fails.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

VALID_CATEGORY_SLUGS = {
    "schools-education", "school-construction", "budget-finance",
    "transportation", "zoning-land-use", "public-safety",
    "policy-governance", "equity-inclusion", "technology",
    "community-parks", "personnel", "general",
}

VALID_URGENCY = {"routine", "notable", "significant"}
MIN_SUMMARY_LEN = 80
MAX_SUMMARY_LEN = 2000
MAX_TITLE_LEN = 300
MAX_DECISIONS = 20
INVALID_PLACEHOLDERS = {"n/a", "none", "unknown", "tbd", ""}


class ValidationError(Exception):
    pass


def validate_item(prompt1: dict, prompt2: dict) -> None:
    """Run all 10 quality checks. Raises ValidationError on first failure."""

    # 1. title is a non-empty string
    title = prompt1.get("title", "")
    if not isinstance(title, str) or not title.strip():
        raise ValidationError("Check 1 failed: 'title' is empty or not a string")

    # 2. title length reasonable
    if len(title) > MAX_TITLE_LEN:
        raise ValidationError(f"Check 2 failed: 'title' exceeds {MAX_TITLE_LEN} chars")

    # 3. summary is a non-empty string
    summary = prompt1.get("summary", "")
    if not isinstance(summary, str) or not summary.strip():
        raise ValidationError("Check 3 failed: 'summary' is empty or not a string")

    # 4. summary meets minimum length
    if len(summary.strip()) < MIN_SUMMARY_LEN:
        raise ValidationError(f"Check 4 failed: 'summary' is too short ({len(summary)} < {MIN_SUMMARY_LEN})")

    # 5. summary does not contain placeholder values
    if summary.strip().lower() in INVALID_PLACEHOLDERS:
        raise ValidationError("Check 5 failed: 'summary' contains invalid placeholder content")

    # 6. decisions is a list (may be empty)
    decisions = prompt1.get("decisions", [])
    if not isinstance(decisions, list):
        raise ValidationError("Check 6 failed: 'decisions' is not a list")
    if len(decisions) > MAX_DECISIONS:
        raise ValidationError(f"Check 6 failed: 'decisions' has more than {MAX_DECISIONS} entries")

    # 7. action_items is a list (may be empty)
    action_items = prompt1.get("action_items", [])
    if not isinstance(action_items, list):
        raise ValidationError("Check 7 failed: 'action_items' is not a list")

    # 8. primary_category is a valid slug
    primary_category = prompt2.get("primary_category", "")
    if primary_category not in VALID_CATEGORY_SLUGS:
        raise ValidationError(f"Check 8 failed: 'primary_category' '{primary_category}' is not valid")

    # 9. urgency is a valid value
    urgency = prompt2.get("urgency", "")
    if urgency not in VALID_URGENCY:
        raise ValidationError(f"Check 9 failed: 'urgency' '{urgency}' is not valid (must be routine/notable/significant)")

    # 10. fiscal_impact is a boolean
    fiscal_impact = prompt2.get("fiscal_impact")
    if not isinstance(fiscal_impact, bool):
        raise ValidationError(f"Check 10 failed: 'fiscal_impact' must be a boolean, got {type(fiscal_impact)}")

    logger.debug("All 10 validation checks passed for item: %s", title[:60])
