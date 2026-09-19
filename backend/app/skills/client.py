"""
Skill Memory Client for TeachMind AI Agent.
Consumes persistent SkillService and database repository for semantic search and storage.
"""

from typing import List, Dict, Any, Optional
from backend.db.database import SessionLocal
from backend.repositories.skill_repository import SkillRepository
from backend.services.embedding_service import get_default_embedding_provider
from backend.services.skill_service import SkillService
from backend.schemas.skill import SearchRequest, SkillCreate, SkillUpdate, SkillResponse
from backend.app.schemas.agent import SkillSummary as AgentSkillSummary
from backend.app.skills.adapter import (
    canonical_to_agent_summary,
    agent_summary_to_canonical_create,
    agent_summary_to_canonical_update,
)


class SkillMemoryClient:
    """Direct programmatic adapter to persistent Skill Memory subsystem."""

    def _get_service(self, db) -> SkillService:
        repo = SkillRepository(db)
        provider = get_default_embedding_provider()
        return SkillService(repo, provider)

    def search_skills(self, query: str, user_id: str = "user_default", top_k: int = 3) -> Dict[str, Any]:
        """
        Executes semantic skill search via persistent SkillService.
        Returns dictionary matching POST /skills/search contract:
        { "query": "...", "results": [ { "skill_id": "...", "name": "...", "similarity": 0.91, "skill": {...} } ] }
        """
        db = SessionLocal()
        try:
            service = self._get_service(db)
            search_resp = service.search_skills(SearchRequest(query=query, top_k=top_k))
            return search_resp.model_dump()
        finally:
            db.close()

    def store_skill(self, skill: AgentSkillSummary, user_id: str = "user_default") -> AgentSkillSummary:
        """Stores a new learned skill in persistent database.

        If the skill already exists (by scoped skill_id), updates it instead.
        """
        db = SessionLocal()
        try:
            service = self._get_service(db)
            skill_create = agent_summary_to_canonical_create(skill, user_id=user_id)
            try:
                resp = service.store_skill(skill_create)
                return canonical_to_agent_summary(resp)
            except ValueError:
                # Skill already exists — look it up by its canonical scoped skill_id
                # so that update_skill uses the correct DB identifier (not skill.id default).
                repo = SkillRepository(db)
                existing = repo.get_by_id(skill_create.skill_id)
                if existing is None:
                    raise
                skill_update = agent_summary_to_canonical_update(skill)
                resp = service.update_skill(existing.skill_id, skill_update)
                return canonical_to_agent_summary(resp)
        finally:
            db.close()

    def update_skill(self, skill: AgentSkillSummary, user_id: str = "user_default") -> AgentSkillSummary:
        """Applies a correction/update to an existing skill and increments its version."""
        db = SessionLocal()
        try:
            service = self._get_service(db)
            skill_update = agent_summary_to_canonical_update(skill)
            resp = service.update_skill(skill.id, skill_update)
            return canonical_to_agent_summary(resp)
        finally:
            db.close()

    def get_skill_by_name(self, name: str, user_id: str = "user_default") -> Optional[AgentSkillSummary]:
        """Looks up a skill by exact or normalized name."""
        db = SessionLocal()
        try:
            repo = SkillRepository(db)
            skills = repo.get_all()
            for s in skills:
                if s.name.lower() == name.lower() or s.skill_id.lower() == name.lower():
                    provider = get_default_embedding_provider()
                    service = SkillService(repo, provider)
                    return canonical_to_agent_summary(service._to_response(s))
            return None
        finally:
            db.close()

    def list_skills(self, user_id: str = "user_default") -> List[AgentSkillSummary]:
        """Lists all active skills from persistent database."""
        db = SessionLocal()
        try:
            repo = SkillRepository(db)
            skills = repo.get_all()
            provider = get_default_embedding_provider()
            service = SkillService(repo, provider)
            return [canonical_to_agent_summary(service._to_response(s)) for s in skills]
        finally:
            db.close()


skill_memory_client = SkillMemoryClient()
