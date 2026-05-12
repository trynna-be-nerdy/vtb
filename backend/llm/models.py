from typing import Optional
from pydantic import BaseModel, Field, field_validator

VALID_CATEGORIES = {
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
}

VALID_URGENCY = {"routine", "notable", "significant"}


class KeyFigures(BaseModel):
    amounts: list[str] = Field(default_factory=list)
    vote_tallies: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    schools: list[str] = Field(default_factory=list)


class ContentRewriteResult(BaseModel):
    title: str
    summary: str
    decisions: list[str] = Field(default_factory=list)
    action_items: list[str] = Field(default_factory=list)
    key_figures: KeyFigures = Field(default_factory=KeyFigures)

    @field_validator("title")
    @classmethod
    def title_max_ten_words(cls, v: str) -> str:
        words = v.split()
        if len(words) > 10:
            return " ".join(words[:10])
        return v

    @field_validator("key_figures", mode="before")
    @classmethod
    def coerce_key_figures(cls, v):
        if isinstance(v, dict):
            return KeyFigures(**v)
        return v


class ClassificationResult(BaseModel):
    primary_category: str
    secondary_tags: list[str] = Field(default_factory=list)
    urgency: str
    fiscal_impact: bool
    affects_schools: list[str] = Field(default_factory=list)

    @field_validator("primary_category")
    @classmethod
    def must_be_valid_category(cls, v: str) -> str:
        if v not in VALID_CATEGORIES:
            return "general"
        return v

    @field_validator("urgency")
    @classmethod
    def must_be_valid_urgency(cls, v: str) -> str:
        v = v.lower()
        if v not in VALID_URGENCY:
            return "routine"
        return v


class MeetingOverviewResult(BaseModel):
    meeting_overview: str
    top_decisions: list[str] = Field(default_factory=list)
    fiscal_total: Optional[str] = None
    next_meeting_notes: Optional[str] = None

    @field_validator("top_decisions")
    @classmethod
    def cap_at_three(cls, v: list[str]) -> list[str]:
        return v[:3]
