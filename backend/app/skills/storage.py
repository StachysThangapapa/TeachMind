"""
Persistent Procedural Skill Memory Storage for TeachMind.
Persists skills to disk (backend/app/data/skills.json) to survive backend server restarts.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from backend.app.schemas.agent import SkillSummary


class SkillStorage:
    """Persistent storage engine for learned TeachMind skills."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            storage_path = data_dir / "skills.json"
        
        self.storage_path = storage_path
        self._skills: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        """Load stored skills from persistent JSON file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self._skills = json.load(f)
            except Exception as e:
                print(f"[SkillStorage Warning] Error loading skills.json: {e}")
                self._skills = {}
        else:
            self._skills = {}

    def _save(self):
        """Save active skills to persistent JSON file."""
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._skills, f, indent=2)
        except Exception as e:
            print(f"[SkillStorage Error] Error saving skills.json: {e}")

    def store_skill(self, skill: SkillSummary, user_id: str = "user_default") -> SkillSummary:
        """Store or update a skill in persistent memory."""
        key = f"{user_id}:{skill.name}"
        data = skill.model_dump()
        data["user_id"] = user_id
        self._skills[key] = data
        self._save()
        return skill

    def get_skill_by_name(self, name: str, user_id: str = "user_default") -> Optional[SkillSummary]:
        """Fetch a stored skill by name."""
        key = f"{user_id}:{name}"
        if key in self._skills:
            return SkillSummary(**self._skills[key])
        return None

    def list_skills(self, user_id: str = "user_default") -> List[SkillSummary]:
        """List all stored skills for a user."""
        results = []
        for key, val in self._skills.items():
            if key.startswith(f"{user_id}:") or val.get("user_id") == user_id:
                results.append(SkillSummary(**val))
        return results

    def search_similar(self, query: str, user_id: str = "user_default", top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform semantic / trigger similarity search over persistent skills.
        """
        q_lower = query.lower()
        user_skills = self.list_skills(user_id)
        scored_candidates = []

        for skill in user_skills:
            score = 0.0
            # Trigger match scoring
            for trigger in skill.triggers:
                if trigger.lower() in q_lower or q_lower in trigger.lower():
                    score = max(score, 0.94)
            # Keyword / name match scoring
            if skill.name.replace("_", " ") in q_lower:
                score = max(score, 0.91)
            elif any(w in q_lower for w in skill.name.split("_")):
                score = max(score, 0.85)

            if score > 0.0:
                scored_candidates.append({
                    "skill_id": skill.id,
                    "name": skill.name,
                    "similarity": score,
                    "skill": {
                        "description": skill.description,
                        "triggers": skill.triggers,
                        "steps": skill.steps,
                        "rules": skill.rules,
                        "exceptions": skill.exceptions,
                        "version": skill.version,
                        "confidence": skill.confidence
                    }
                })

        scored_candidates.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_candidates[:top_k]


skill_storage = SkillStorage()
