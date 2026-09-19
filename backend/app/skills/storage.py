"""
Persistent Procedural Skill Memory Storage for TeachMind.
Delegates directly to persistent SkillMemoryClient / database.
"""

from typing import Dict, Any, List, Optional
from backend.app.schemas.agent import SkillSummary
from backend.app.skills.client import skill_memory_client


class SkillStorage:
    """Wrapper delegating to canonical Skill Memory database."""

    def store_skill(self, skill: SkillSummary, user_id: str = "user_default") -> SkillSummary:
        return skill_memory_client.store_skill(skill, user_id=user_id)

    def get_skill_by_name(self, name: str, user_id: str = "user_default") -> Optional[SkillSummary]:
        return skill_memory_client.get_skill_by_name(name, user_id=user_id)

    def list_skills(self, user_id: str = "user_default") -> List[SkillSummary]:
        return skill_memory_client.list_skills(user_id=user_id)

    def search_similar(self, query: str, user_id: str = "user_default", top_k: int = 3) -> List[Dict[str, Any]]:
        search_res = skill_memory_client.search_skills(query, user_id=user_id, top_k=top_k)
        return search_res.get("results", [])


skill_storage = SkillStorage()
