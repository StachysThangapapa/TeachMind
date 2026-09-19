"""Skill-Memory business logic.

Orchestrates validation, embedding generation, versioning, and repository
calls.  This layer is the single authority for the TeachMind loop:

    Teach → Store → Retrieve → Correct → Verify → Reuse
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from backend.models.skill import Skill, SkillVersion
from backend.repositories.skill_repository import SkillRepository
from backend.schemas.skill import (
    MetadataSchema,
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    SkillCreate,
    SkillListResponse,
    SkillResponse,
    SkillSummary,
    SkillUpdate,
    SkillVersionResponse,
)
from backend.services.embedding_service import EmbeddingProvider, build_embedding_text


class SkillService:
    """Core Skill-Memory operations."""

    def __init__(
        self,
        repository: SkillRepository,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._repo = repository
        self._embed = embedding_provider

    # ── Store ──────────────────────────────────────────────────────

    def store_skill(self, data: SkillCreate) -> SkillResponse:
        """Validate, embed, and persist a new skill.

        Raises ``ValueError`` if a skill with the same ID already exists.
        """
        if self._repo.get_by_id(data.skill_id):
            raise ValueError(f"Skill '{data.skill_id}' already exists")

        # Serialise Pydantic sub-models → plain dicts for JSONB storage
        steps = [s.model_dump() for s in data.steps]
        rules = [r.model_dump() for r in data.rules]
        examples = [e.model_dump() for e in data.examples]

        # Build embedding
        embedding_text = build_embedding_text(
            {
                "name": data.name,
                "description": data.description,
                "triggers": data.triggers,
                "steps": steps,
                "rules": rules,
                "examples": examples,
            }
        )
        embedding = self._embed.embed_document(embedding_text)

        now = datetime.now(timezone.utc)

        skill = Skill(
            skill_id=data.skill_id,
            name=data.name,
            description=data.description,
            triggers=data.triggers,
            steps=steps,
            rules=rules,
            examples=examples,
            version=data.version,
            verified=data.verified,
            embedding=embedding,
            created_at=now,
            updated_at=now,
        )
        skill = self._repo.create(skill)

        # Record initial version in history
        self._save_version_snapshot(skill)

        return self._to_response(skill)

    # ── Search ─────────────────────────────────────────────────────

    def search_skills(self, request: SearchRequest) -> SearchResponse:
        """Semantic skill retrieval via pgvector cosine similarity."""
        query_embedding = self._embed.embed_query(request.query)
        rows = self._repo.search_by_embedding(query_embedding, request.top_k)

        results: list[SearchResultItem] = []
        for row in rows:
            skill_resp = SkillResponse(
                skill_id=row["skill_id"],
                name=row["name"],
                description=row["description"],
                triggers=row["triggers"],
                steps=row["steps"],
                rules=row["rules"],
                examples=row["examples"],
                version=row["version"],
                verified=row["verified"],
                metadata=MetadataSchema(
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                ),
            )
            results.append(
                SearchResultItem(
                    skill_id=row["skill_id"],
                    name=row["name"],
                    similarity=round(float(row["similarity"]), 4),
                    skill=skill_resp,
                )
            )

        return SearchResponse(query=request.query, results=results)

    # ── Update / Correct ───────────────────────────────────────────

    def update_skill(self, skill_id: str, data: SkillUpdate) -> SkillResponse:
        """Apply a partial correction to an existing skill.

        * Only fields present in ``data`` are changed.
        * ``version`` is incremented automatically.
        * The embedding is regenerated.
        * A snapshot is saved to ``skill_versions``.
        """
        skill = self._repo.get_by_id(skill_id)
        if skill is None:
            raise ValueError(f"Skill '{skill_id}' not found")

        updates = data.model_dump(exclude_unset=True)

        # Serialise nested Pydantic models that came through validation
        if "steps" in updates and updates["steps"] is not None:
            updates["steps"] = [
                s.model_dump() if hasattr(s, "model_dump") else s
                for s in updates["steps"]
            ]
        if "rules" in updates and updates["rules"] is not None:
            updates["rules"] = [
                r.model_dump() if hasattr(r, "model_dump") else r
                for r in updates["rules"]
            ]
        if "examples" in updates and updates["examples"] is not None:
            updates["examples"] = [
                e.model_dump() if hasattr(e, "model_dump") else e
                for e in updates["examples"]
            ]

        for field, value in updates.items():
            setattr(skill, field, value)

        skill.version += 1
        skill.updated_at = datetime.now(timezone.utc)

        # Regenerate embedding from the (now-updated) skill content
        embedding_text = build_embedding_text(
            {
                "name": skill.name,
                "description": skill.description,
                "triggers": skill.triggers,
                "steps": skill.steps,
                "rules": skill.rules,
                "examples": skill.examples,
            }
        )
        skill.embedding = self._embed.embed_document(embedding_text)

        skill = self._repo.update(skill)
        self._save_version_snapshot(skill)

        return self._to_response(skill)

    # ── Verify ─────────────────────────────────────────────────────

    def verify_skill(self, skill_id: str) -> SkillResponse:
        """Mark a skill as verified by the user."""
        skill = self._repo.get_by_id(skill_id)
        if skill is None:
            raise ValueError(f"Skill '{skill_id}' not found")

        skill.verified = True
        skill.updated_at = datetime.now(timezone.utc)
        skill = self._repo.update(skill)
        return self._to_response(skill)

    # ── Single retrieval ───────────────────────────────────────────

    def get_skill(self, skill_id: str) -> Optional[SkillResponse]:
        """Return a single skill or ``None``."""
        skill = self._repo.get_by_id(skill_id)
        if skill is None:
            return None
        return self._to_response(skill)

    # ── List ───────────────────────────────────────────────────────

    def list_skills(self) -> SkillListResponse:
        """Return summary information for all stored skills."""
        skills = self._repo.get_all()
        return SkillListResponse(
            skills=[
                SkillSummary(
                    skill_id=s.skill_id,
                    name=s.name,
                    verified=s.verified,
                    version=s.version,
                )
                for s in skills
            ]
        )

    # ── Version history ────────────────────────────────────────────

    def get_skill_versions(self, skill_id: str) -> List[SkillVersionResponse]:
        """Return the full version history for a skill."""
        versions = self._repo.get_versions(skill_id)
        return [
            SkillVersionResponse(
                skill_id=v.skill_id,
                version=v.version,
                name=v.name,
                description=v.description,
                triggers=v.triggers,
                steps=v.steps,
                rules=v.rules,
                examples=v.examples,
                verified=v.verified,
                created_at=v.created_at,
            )
            for v in versions
        ]

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _to_response(skill: Skill) -> SkillResponse:
        """Convert an ORM ``Skill`` to the canonical response schema."""
        return SkillResponse(
            skill_id=skill.skill_id,
            name=skill.name,
            description=skill.description,
            triggers=skill.triggers,
            steps=skill.steps,
            rules=skill.rules,
            examples=skill.examples,
            version=skill.version,
            verified=skill.verified,
            metadata=MetadataSchema(
                created_at=skill.created_at,
                updated_at=skill.updated_at,
            ),
        )

    def _save_version_snapshot(self, skill: Skill) -> None:
        """Append an immutable version record for the current skill state."""
        self._repo.create_version(
            SkillVersion(
                skill_id=skill.skill_id,
                version=skill.version,
                name=skill.name,
                description=skill.description,
                triggers=skill.triggers,
                steps=skill.steps,
                rules=skill.rules,
                examples=skill.examples,
                verified=skill.verified,
            )
        )
