"""
Workflow Planner for TeachMind AI Agent.
Plans execution steps and composes multiple skills for complex user requests.
"""

from typing import List, Dict, Any
from backend.app.schemas.agent import SkillSummary, ParsedIntent


class WorkflowPlanner:
    """Creates execution plans and composes skills for multi-domain workflows."""

    def create_plan(self, intent: ParsedIntent, skill: SkillSummary) -> List[str]:
        """Generate structured execution plan steps."""
        if intent.intent == "morning_briefing":
            return [
                "Step 1: Retrieve today's calendar events (get_calendar_events)",
                "Step 2: Retrieve active package deliveries (get_today_deliveries)",
                "Step 3: Filter and prioritize items according to user preferences",
                "Step 4: Format composite morning briefing response"
            ]
        elif "delivery" in skill.name.lower():
            return [
                "Step 1: Search Skill Memory for delivery preferences",
                "Step 2: Execute get_today_deliveries read-only tool",
                "Step 3: Filter active orders and prioritize delayed items",
                "Step 4: Format personalized delivery summary"
            ]
        else:
            return [
                f"Step 1: Execute skill {skill.name}",
                "Step 2: Format personalized response"
            ]


planner = WorkflowPlanner()
