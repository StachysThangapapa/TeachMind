"""
Skill Extraction Engine for TeachMind.
Converts natural-language teaching instructions into structured, reusable procedural skills.
"""

from typing import Dict, Any, List, Optional
from backend.app.schemas.agent import SkillSummary
from backend.app.llm.client import llm_client
from backend.app.llm.prompts import SKILL_EXTRACTION_PROMPT


class SkillExtractor:
    """Transforms user teaching instructions into canonical SkillSummary objects."""

    def extract_skill(self, teaching_instruction: str, user_id: str = "user_default") -> SkillSummary:
        """
        Extracts structured skill from natural language instruction.
        """
        # Call LLM client for structured extraction
        skill = llm_client.generate_structured(
            prompt=teaching_instruction,
            schema=SkillSummary,
            system_prompt=SKILL_EXTRACTION_PROMPT,
            temperature=0.0
        )

        # Fallback enrichment if LLM output requires defaulting
        inst_lower = teaching_instruction.lower()
        if not skill.name or skill.name == "generic_skill":
            if "briefing" in inst_lower:
                skill.name = "personalized_morning_briefing"
                skill.description = "Prepare a personalized morning briefing combining calendar, tasks, and deliveries."
                skill.triggers = ["prepare my morning briefing", "morning briefing", "what do i have today"]
                skill.steps = [
                    {"step": 1, "action": "get_calendar_events", "instruction": "Check calendar events"},
                    {"step": 2, "action": "get_pending_tasks", "instruction": "Check pending tasks"},
                    {"step": 3, "action": "get_today_deliveries", "instruction": "Check package deliveries"}
                ]
                skill.rules = [
                    {"condition": "item is urgent", "action": "mention_first"},
                    {"condition": "delivery is present", "action": "hide_tracking_id_unless_requested"}
                ]
            elif "delivery" in inst_lower or "deliveries" in inst_lower:
                skill.name = "personalized_delivery_summary"
                skill.description = "Summarize today's package deliveries according to user preference."
                skill.triggers = ["check my deliveries", "deliveries today", "package status"]
                skill.steps = [
                    {"step": 1, "action": "get_today_deliveries", "instruction": "Retrieve package status"}
                ]
                skill.rules = [
                    {"condition": "delivery is delayed", "action": "prioritize_first"},
                    {"condition": "tracking requested", "action": "hide_unless_explicit"}
                ]

        if not skill.version:
            skill.version = "1.0"
        if not skill.confidence:
            skill.confidence = 0.90

        return skill


skill_extractor = SkillExtractor()
