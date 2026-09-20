"""Skill-Memory REST API router.

Endpoints
---------
POST   /skills               — store a new skill
POST   /skills/search        — semantic skill retrieval (struct.json contract)
GET    /skills               — list all skills (summaries)
GET    /skills/{skill_id}    — retrieve a single skill
PATCH  /skills/{skill_id}    — correct / update a skill
PATCH  /skills/{skill_id}/verify — mark a skill as verified
GET    /skills/{skill_id}/versions — retrieve version history
"""

from __future__ import annotations

from functools import lru_cache
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.repositories.skill_repository import SkillRepository
from backend.schemas.skill import (
    ExtractRequest,
    ExtractResponse,
    SearchRequest,
    SearchResponse,
    SkillCreate,
    SkillListResponse,
    SkillResponse,
    SkillUpdate,
    SkillVersionResponse,
)
from backend.services.embedding_service import (
    CohereEmbeddingProvider,
    EmbeddingProvider,
)
from backend.services.extraction_service import (
    CohereSkillExtractionProvider,
    SkillExtractionProvider,
)
from backend.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["skills"])


# ── Dependency injection ───────────────────────────────────────────────


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Singleton embedding provider — created once, reused for all requests."""
    return CohereEmbeddingProvider()


@lru_cache
def get_extraction_provider() -> SkillExtractionProvider:
    """Singleton extraction provider — extracts canonical skill JSON via Cohere."""
    return CohereSkillExtractionProvider()


def get_skill_service(
    db: Session = Depends(get_db),
    embedding_provider: EmbeddingProvider = Depends(get_embedding_provider),
) -> SkillService:
    """Per-request service with its own DB session + shared embedding provider."""
    repository = SkillRepository(db)
    return SkillService(repository, embedding_provider)


# ── POST /skills/extract ───────────────────────────────────────────────


@router.post("/extract", response_model=ExtractResponse)
def extract_skill(
    data: ExtractRequest,
    provider: SkillExtractionProvider = Depends(get_extraction_provider),
) -> ExtractResponse:
    """Extract a canonical Skill JSON from natural-language teaching text.

    Uses Cohere structured JSON output and schema enforcement.
    Does NOT store the skill in PostgreSQL (storage is handled by POST /skills).
    """
    try:
        extracted = provider.extract_skill(data.text)
        return ExtractResponse(skill=extracted)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


# ── POST /skills ───────────────────────────────────────────────────────


@router.post("", response_model=SkillResponse, status_code=201)
def store_skill(
    data: SkillCreate,
    service: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    """Validate, embed, and store a new canonical Skill JSON."""
    try:
        return service.store_skill(data)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


# ── POST /skills/search ───────────────────────────────────────────────


@router.post("/search", response_model=SearchResponse)
def search_skills(
    data: SearchRequest,
    service: SkillService = Depends(get_skill_service),
) -> SearchResponse:
    """Semantic skill retrieval — response follows struct.json contract."""
    return service.search_skills(data)


# ── GET /skills ────────────────────────────────────────────────────────


@router.get("", response_model=SkillListResponse)
def list_skills(
    service: SkillService = Depends(get_skill_service),
) -> SkillListResponse:
    """Return summary information for every stored skill."""
    return service.list_skills()


# ── GET /skills/{skill_id} ────────────────────────────────────────────


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: str,
    service: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    """Return a single skill in canonical JSON format."""
    result = service.get_skill(skill_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Skill not found")
    return result


# ── PATCH /skills/{skill_id} ──────────────────────────────────────────


@router.patch("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: str,
    data: SkillUpdate,
    service: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    """Apply a partial correction to an existing skill.

    Automatically increments ``version``, regenerates the embedding,
    and appends a version-history snapshot.
    """
    try:
        return service.update_skill(skill_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ── PATCH /skills/{skill_id}/verify ───────────────────────────────────


@router.patch("/{skill_id}/verify", response_model=SkillResponse)
def verify_skill(
    skill_id: str,
    service: SkillService = Depends(get_skill_service),
) -> SkillResponse:
    """Mark a skill as verified by the user."""
    try:
        return service.verify_skill(skill_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


# ── GET /skills/{skill_id}/versions ───────────────────────────────────


@router.get("/{skill_id}/versions", response_model=List[SkillVersionResponse])
def get_skill_versions(
    skill_id: str,
    service: SkillService = Depends(get_skill_service),
) -> List[SkillVersionResponse]:
    """Return the complete version history for a skill."""
    versions = service.get_skill_versions(skill_id)
    if not versions:
        raise HTTPException(status_code=404, detail="Skill not found or has no history")
    return versions
