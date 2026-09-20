"""Pydantic request / response models for the Skill-Memory API.

Every model here maps directly to the agreed canonical Skill JSON contract
and the search-response contract defined in docs/struct.json.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ── Sub-schemas matching the canonical Skill JSON ──────────────────────


class StepSchema(BaseModel):
    """A single ordered workflow instruction."""

    step: int
    instruction: str


class RuleSchema(BaseModel):
    """A conditional instruction."""

    condition: str
    action: str


class ExampleSchema(BaseModel):
    """An example input paired with its expected behaviour."""

    input: str
    expected_behavior: str


class MetadataSchema(BaseModel):
    """Timestamp metadata nested inside the canonical Skill JSON."""

    created_at: datetime
    updated_at: datetime


# ── Request schemas ────────────────────────────────────────────────────


class SkillCreate(BaseModel):
    """POST /skills — store a new skill.

    Matches the canonical Skill JSON *without* metadata (the server
    generates created_at / updated_at).
    """

    skill_id: str = Field(..., description="Unique skill identifier")
    name: str = Field(..., description="Human-readable skill name")
    description: str = Field("", description="Description of the workflow")
    triggers: List[str] = Field(
        default_factory=list,
        description="Phrases that indicate when this skill should be used",
    )
    steps: List[StepSchema] = Field(
        default_factory=list, description="Ordered workflow instructions"
    )
    rules: List[RuleSchema] = Field(
        default_factory=list, description="Conditional instructions"
    )
    examples: List[ExampleSchema] = Field(
        default_factory=list,
        description="Example inputs and expected behaviour",
    )
    version: int = Field(1, description="Skill version")
    verified: bool = Field(False, description="Whether the user verified the skill")


class SkillUpdate(BaseModel):
    """PATCH /skills/{skill_id} — partial correction / update.

    Only the fields provided will be changed; omitted fields keep their
    current value.  ``version`` is incremented automatically by the
    service layer.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    triggers: Optional[List[str]] = None
    steps: Optional[List[StepSchema]] = None
    rules: Optional[List[RuleSchema]] = None
    examples: Optional[List[ExampleSchema]] = None
    verified: Optional[bool] = None


class SearchRequest(BaseModel):
    """POST /skills/search — semantic skill retrieval."""

    query: str
    top_k: int = Field(3, ge=1, le=50)


# ── Response schemas ───────────────────────────────────────────────────


class SkillResponse(BaseModel):
    """Canonical Skill JSON returned by all single-skill endpoints.

    Matches the shape defined in §4 of the spec and inside the ``skill``
    object of the struct.json search-response contract.
    """

    skill_id: str
    name: str
    description: str
    triggers: List[str]
    steps: List[StepSchema]
    rules: List[RuleSchema]
    examples: List[ExampleSchema]
    version: int
    verified: bool
    metadata: MetadataSchema


class SearchResultItem(BaseModel):
    """One result inside the POST /skills/search response.

    Follows the struct.json contract verbatim — ``skill_id`` and ``name``
    appear both at the result level *and* inside the nested ``skill``.
    """

    skill_id: str
    name: str
    similarity: float
    skill: SkillResponse


class SearchResponse(BaseModel):
    """POST /skills/search response — matches struct.json exactly."""

    query: str
    results: List[SearchResultItem]


class SkillSummary(BaseModel):
    """Lightweight skill info for the GET /skills list endpoint."""

    skill_id: str
    name: str
    verified: bool
    version: int


class SkillListResponse(BaseModel):
    """GET /skills response."""

    skills: List[SkillSummary]


class SkillVersionResponse(BaseModel):
    """A single historical version of a skill."""

    skill_id: str
    version: int
    name: str
    description: str
    triggers: List[str]
    steps: List[StepSchema]
    rules: List[RuleSchema]
    examples: List[ExampleSchema]
    verified: bool
    created_at: datetime


class ExtractRequest(BaseModel):
    """POST /skills/extract request."""

    text: str = Field(..., min_length=1, description="Natural language teaching instruction from the user")


class ExtractResponse(BaseModel):
    """POST /skills/extract response containing complete canonical Skill JSON."""

    skill: SkillResponse

