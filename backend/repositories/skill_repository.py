"""Database access layer for the ``skills`` and ``skill_versions`` tables.

All raw SQL / ORM queries live here.  The service layer never touches the
database directly.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.models.skill import Skill, SkillVersion


class SkillRepository:
    """CRUD + pgvector similarity search for skills."""

    def __init__(self, db: Session) -> None:
        self._db = db

    # ── Skill CRUD ─────────────────────────────────────────────────

    def create(self, skill: Skill) -> Skill:
        """Insert a new skill and return the managed instance."""
        self._db.add(skill)
        self._db.commit()
        self._db.refresh(skill)
        return skill

    def get_by_id(self, skill_id: str) -> Optional[Skill]:
        """Return a single skill by its ID, or ``None``."""
        return self._db.query(Skill).filter(Skill.skill_id == skill_id).first()

    def get_all(self) -> List[Skill]:
        """Return every skill (current version only)."""
        return self._db.query(Skill).order_by(Skill.created_at).all()

    def update(self, skill: Skill) -> Skill:
        """Flush pending attribute changes and return the refreshed instance."""
        self._db.commit()
        self._db.refresh(skill)
        return skill

    def delete(self, skill: Skill) -> None:
        """Remove a skill row."""
        self._db.delete(skill)
        self._db.commit()

    # ── pgvector similarity search ─────────────────────────────────

    def search_by_embedding(
        self,
        query_embedding: List[float],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """Cosine-similarity search via pgvector (with Python cosine fallback for non-pgvector backends).

        Returns rows ordered by descending similarity with a computed
        ``similarity`` column (1 − cosine distance).
        """
        try:
            result = self._db.execute(
                text(
                    """
                    SELECT skill_id,
                           name,
                           description,
                           triggers,
                           steps,
                           rules,
                           examples,
                           version,
                           verified,
                           created_at,
                           updated_at,
                           1 - (embedding <=> :qvec ::vector) AS similarity
                    FROM   skills
                    WHERE  embedding IS NOT NULL
                    ORDER  BY embedding <=> :qvec ::vector
                    LIMIT  :top_k
                    """
                ),
                {"qvec": str(query_embedding), "top_k": top_k},
            )
            return [dict(row._mapping) for row in result]
        except Exception:
            # Fallback for SQLite / non-pgvector environments
            skills = self.get_all()
            scored = []
            for s in skills:
                sim = 0.0
                if s.embedding is not None and len(s.embedding) == len(query_embedding):
                    # Compute cosine similarity in Python
                    dot = sum(a * b for a, b in zip(s.embedding, query_embedding))
                    norm_a = math.sqrt(sum(a * a for a in s.embedding))
                    norm_b = math.sqrt(sum(b * b for b in query_embedding))
                    if norm_a > 0 and norm_b > 0:
                        sim = dot / (norm_a * norm_b)
                scored.append({
                    "skill_id": s.skill_id,
                    "name": s.name,
                    "description": s.description,
                    "triggers": s.triggers,
                    "steps": s.steps,
                    "rules": s.rules,
                    "examples": s.examples,
                    "version": s.version,
                    "verified": s.verified,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                    "similarity": sim
                })
            scored.sort(key=lambda x: x["similarity"], reverse=True)
            return scored[:top_k]

    # ── Version history ────────────────────────────────────────────

    def create_version(self, version: SkillVersion) -> SkillVersion:
        """Append a version-history snapshot."""
        self._db.add(version)
        self._db.commit()
        self._db.refresh(version)
        return version

    def get_versions(self, skill_id: str) -> List[SkillVersion]:
        """Return all version snapshots for a skill, oldest first."""
        return (
            self._db.query(SkillVersion)
            .filter(SkillVersion.skill_id == skill_id)
            .order_by(SkillVersion.version)
            .all()
        )
