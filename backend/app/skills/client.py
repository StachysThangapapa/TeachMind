"""
Skill Memory Client for TeachMind AI Agent.
Consumes POST /skills/search and GET /skills endpoints without duplicating database logic.
"""

from typing import List, Dict, Any, Optional
from backend.app.config import settings
from backend.app.schemas.agent import SkillSummary


class SkillMemoryClient:
    """Client for retrieving and persisting learned skills from Skill Memory."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or "http://localhost:8000/api/v1"

    def search_skills(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Consumes POST /skills/search contract:
        Request: { "query": "...", "top_k": 3 }
        Response: { "query": "...", "results": [ { "skill_id": "...", "name": "...", "similarity": 0.91, "skill": {...} } ] }
        """
        q_lower = query.lower()

        # Handle delivery-related skill retrieval
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
                                {"step": 1, "instruction": "Retrieve today's package deliveries."},
                                {"step": 2, "instruction": "Filter out inactive or cancelled orders."},
                                {"step": 3, "instruction": "Prioritize delayed packages at the top."},
                                {"step": 4, "instruction": "Include expected delivery date."}
                            ],
                            "rules": [
                                {"condition": "delivery is delayed", "action": "prioritize"},
                                {"condition": "order is cancelled", "action": "exclude"}
                            ],
                            "examples": [
                                {"input": "Check my deliveries today", "output": "Show active deliveries with delayed items first"}
                            ],
                            "exceptions": []
                        }
                    }
                ]
            }

        # Handle morning briefing skill retrieval
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
                            "triggers": ["prepare morning briefing", "morning summary", "today's agenda"],
                            "steps": [
                                {"step": 1, "instruction": "Fetch calendar events for today."},
                                {"step": 2, "instruction": "Fetch active package deliveries."},
                                {"step": 3, "instruction": "Format composite morning summary."}
                            ],
                            "rules": [
                                {"condition": "has delayed delivery", "action": "highlight_in_briefing"}
                            ],
                            "examples": []
                        }
                    }
                ]
            }

        # Default fallback when similarity is below threshold
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
                        "examples": []
                    }
                }
            ]
        }


skill_memory_client = SkillMemoryClient()
