"""
Personalization Engine for TeachMind Agent.
Evaluates personalized skill match scoring and detects preference conflicts.
"""

from typing import Dict, Any, Tuple, Optional
from backend.app.schemas.agent import PersonalContext, SkillSummary


class PersonalizationEngine:
    """Scores skill match against user preferences and detects preference drift/conflicts."""

    def evaluate_match(self, skill: SkillSummary, context: PersonalContext) -> float:
        """
        Calculates personalization match score (0.0 to 1.0) based on user preferences.
        """
        score = 0.85
        prefs = context.preferences.delivery

        # Bonus for skills matching user's active delivery preference
        if "delivery" in skill.name.lower():
            if prefs.get("prioritize_delayed", True):
                score += 0.05
            if prefs.get("show_tracking_id") == "only_if_delayed":
                score += 0.04

        return min(round(score, 2), 0.99)

    def detect_conflict(self, old_value: Any, new_value: Any, domain: str = "delivery") -> Optional[Dict[str, Any]]:
        """
        Detects conflicting preferences (e.g. 'always show tracking IDs' vs 'show tracking IDs only when delayed').
        """
        if old_value != new_value and old_value is not None:
            return {
                "status": "preference_conflict",
                "domain": domain,
                "message": f"Your recent instruction conflicts with an earlier saved {domain} preference.",
                "conflict": {
                    "old_preference": old_value,
                    "new_preference": new_value
                },
                "requires_confirmation": True
            }
        return None


personalization_engine = PersonalizationEngine()
