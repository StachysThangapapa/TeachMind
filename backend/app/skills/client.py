"""
Skill Memory Client for TeachMind AI Agent.
Consumes persistent SkillStorage and returns search results matching POST /skills/search.
"""

from typing import List, Dict, Any, Optional
from backend.app.schemas.agent import SkillSummary
from backend.app.skills.storage import skill_storage


class SkillMemoryClient:
    """Client for retrieving and persisting learned skills from persistent Skill Memory."""

    def search_skills(self, query: str, user_id: str = "user_default", top_k: int = 3) -> Dict[str, Any]:
        """
        Consumes POST /skills/search contract:
        Request: { "query": "...", "top_k": 3 }
        Response: { "query": "...", "results": [ { "skill_id": "...", "name": "...", "similarity": 0.91, "skill": {...} } ] }
        """
        # First query persistent storage
        results = skill_storage.search_similar(query, user_id=user_id, top_k=top_k)
        
        if results:
            return {"query": query, "results": results}

        q_lower = query.lower()

        # Built-in seed skill fallback if storage is empty on first run
        if "delivery" in q_lower or "deliveries" in q_lower or "tracking" in q_lower or "package" in q_lower:
            return {
                "query": query,
                "results": [
                    {
                        "skill_id": "skill_delivery_001",
                        "name": "personalized_delivery_summary",
                        "similarity": 0.94,
                        "skill": {
                            "description": "Summarize today's package deliveries according to user preference.",
                            "triggers": ["check deliveries", "today's deliveries", "package status"],
                            "steps": [
                                {"step": 1, "action": "get_today_deliveries", "instruction": "Retrieve today's package deliveries."}
                            ],
                            "rules": [
                                {"condition": "delivery is delayed", "action": "prioritize"},
                                {"condition": "order is cancelled", "action": "exclude"}
                            ],
                            "examples": [],
                            "exceptions": []
                        }
                    }
                ]
            }

        if "briefing" in q_lower or "morning" in q_lower or "agenda" in q_lower:
            return {
                "query": query,
                "results": [
                    {
                        "skill_id": "skill_briefing_002",
                        "name": "personalized_morning_briefing",
                        "similarity": 0.92,
                        "skill": {
                            "description": "Compose morning briefing combining calendar meetings, pending tasks, and delivery updates.",
                            "triggers": ["prepare my morning briefing", "morning briefing", "what do i have today"],
                            "steps": [
                                {"step": 1, "action": "get_calendar_events", "instruction": "Fetch calendar events for today."},
                                {"step": 2, "action": "get_pending_tasks", "instruction": "Fetch pending tasks."},
                                {"step": 3, "action": "get_today_deliveries", "instruction": "Fetch active package deliveries."}
                            ],
                            "rules": [
                                {"condition": "item is urgent", "action": "prioritize_first"}
                            ],
                            "examples": [],
                            "exceptions": []
                        }
                    }
                ]
            }

        # Fallback when similarity is below threshold
        return {
            "query": query,
            "results": [
                {
                    "skill_id": "skill_generic_000",
                    "name": "generic_assistance",
                    "similarity": 0.45,
                    "skill": {
                        "description": "Generic assistant fallback.",
                        "triggers": [],
                        "steps": [],
                        "rules": [],
                        "examples": [],
                        "exceptions": []
                    }
                }
            ]
        }

    def store_skill(self, skill: SkillSummary, user_id: str = "user_default") -> SkillSummary:
        """Store a newly learned skill in persistent memory."""
        return skill_storage.store_skill(skill, user_id=user_id)


skill_memory_client = SkillMemoryClient()
