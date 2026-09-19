"""
Dynamic Workflow Planner for TeachMind AI Agent.
Generates execution plans and selects dynamic tools from ToolRegistry based on user tasks.
"""

from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.agent import SkillSummary, ParsedIntent, PersonalContext
from backend.app.tools.registry import tool_registry
from backend.app.llm.client import llm_client
from backend.app.llm.prompts import DYNAMIC_PLANNING_PROMPT


class DynamicPlanOutput(BaseModel):
    plan: List[str] = Field(default_factory=list)
    selected_tools: List[str] = Field(default_factory=list)
    tool_arguments: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    reasoning: str = ""


class WorkflowPlanner:
    """Generates execution plans and selects tools dynamically."""

    def plan_and_select_tools(
        self,
        query: str,
        intent: ParsedIntent,
        skill: Optional[SkillSummary] = None,
        context: Optional[PersonalContext] = None
    ) -> DynamicPlanOutput:
        """
        Dynamically plans execution steps and selects required tools.
        """
        q_lower = query.lower()
        available_tools = tool_registry.list_tool_names()

        # Check for Math / Calculator calculation task
        if any(c in q_lower for c in ["%", "+", "-", "*", "/", "calculate", "math", "increase from"]) or intent.intent == "calculator":
            return DynamicPlanOutput(
                plan=["Step 1: Execute calculator tool on mathematical expression"],
                selected_tools=["calculator"],
                tool_arguments={"calculator": {"expression": query}},
                reasoning="Calculation request identified; selecting calculator tool."
            )

        # Check for Date / Time lookup task
        if any(w in q_lower for w in ["date", "clock", "day of the week", "time is it"]):
            return DynamicPlanOutput(
                plan=["Step 1: Execute datetime_tool to retrieve current system date/time"],
                selected_tools=["datetime_tool"],
                tool_arguments={"datetime_tool": {"query": query}},
                reasoning="System date/time request identified; selecting datetime_tool."
            )

        # Check for Morning Briefing task
        if "briefing" in q_lower or intent.intent == "morning_briefing":
            return DynamicPlanOutput(
                plan=[
                    "Step 1: Fetch calendar events (get_calendar_events)",
                    "Step 2: Fetch pending tasks (get_pending_tasks)",
                    "Step 3: Fetch active deliveries (get_today_deliveries)",
                    "Step 4: Format composite morning briefing"
                ],
                selected_tools=["get_calendar_events", "get_pending_tasks", "get_today_deliveries"],
                tool_arguments={
                    "get_calendar_events": {"date": "today"},
                    "get_pending_tasks": {"user_id": context.user_id if context else "user_default"},
                    "get_today_deliveries": {"date": "today"}
                },
                reasoning="Morning briefing task requires composite tool execution across calendar, tasks, and deliveries."
            )

        # Check for Package Delivery task
        if "delivery" in q_lower or "deliveries" in q_lower or "package" in q_lower:
            return DynamicPlanOutput(
                plan=[
                    "Step 1: Retrieve today's package status (get_today_deliveries)",
                    "Step 2: Apply user personalization rules and response formatting"
                ],
                selected_tools=["get_today_deliveries"],
                tool_arguments={"get_today_deliveries": {"date": "today"}},
                reasoning="Package delivery lookup task identified."
            )

        # Unsupported capability check (e.g. Email, Slack)
        if any(w in q_lower for w in ["email", "slack", "tweet", "sms"]):
            return DynamicPlanOutput(
                plan=[],
                selected_tools=[],
                tool_arguments={},
                reasoning="Unsupported external capability requested; no matching tool in allow-list."
            )

        # Fallback LLM structured plan generation
        prompt = f"User Request: '{query}'. Intent: '{intent.intent}'. Available Tools: {available_tools}."
        llm_out = llm_client.generate_structured(
            prompt=prompt,
            schema=DynamicPlanOutput,
            system_prompt=DYNAMIC_PLANNING_PROMPT.format(available_tools=available_tools),
            temperature=0.0
        )

        return llm_out


planner = WorkflowPlanner()
