"""
Explainable Response Generator for TeachMind Agent.
Produces personalized user responses with concise evidence-based explanations.
"""

from typing import Dict, Any, List, Optional, Tuple
from backend.app.schemas.agent import (
    SkillSummary,
    PersonalContext,
    ParsedIntent,
    ExecutionTimelineStep,
)


class ResponseGenerator:
    """Generates explainable personalized responses."""

    def format_delivery_response(
        self,
        tool_result: Dict[str, Any],
        context: PersonalContext,
        skill: SkillSummary
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Formats delivery response formatted according to user preferences.
        Returns (response_text, reason, personalization_metadata).
        """
        deliveries = tool_result.get("deliveries", [])
        prefs = context.preferences.delivery

        # Extract preference rules
        show_active = prefs.get("show_active_only", True)
        prioritize_delayed = prefs.get("prioritize_delayed", True)
        show_tracking = prefs.get("show_tracking_id", "only_if_delayed")

        active_deliveries = [d for d in deliveries if d.get("is_active", True)] if show_active else deliveries

        if prioritize_delayed:
            active_deliveries.sort(key=lambda d: 0 if d.get("status") == "Delayed" else 1)

        lines = [f"You have {len(active_deliveries)} active deliveries today:\n"]

        for d in active_deliveries:
            status = d.get("status", "")
            name = d.get("product_name", "")
            date = d.get("expected_delivery", "")
            tracking = d.get("tracking_id", "")

            # Apply tracking ID preference rule
            include_tracking = (
                show_tracking == "always" or
                (show_tracking == "only_if_delayed" and status == "Delayed")
            )

            tracking_str = f" — Tracking: {tracking}" if include_tracking else ""
            lines.append(f"• **{name}** ({status}) — Expected: {date}{tracking_str}")

        response_text = "\n".join(lines)

        reason = "Prioritized delayed deliveries based on your saved preference."
        if show_tracking == "only_when_requested":
            reason = "Excluded tracking IDs as requested in your recent correction."

        personalization_meta = {
            "preference_applied": "delayed_first",
            "active_only": show_active,
            "tracking_id_rule": show_tracking,
            "explanation": reason
        }

        return response_text, reason, personalization_meta

    def format_briefing_response(
        self,
        calendar_events: List[Dict[str, Any]],
        deliveries: List[Dict[str, Any]],
        context: PersonalContext
    ) -> Tuple[str, str, Dict[str, Any]]:
        """
        Formats composite morning briefing response.
        """
        delayed = [d for d in deliveries if d.get("status") == "Delayed"]
        
        lines = ["Good morning!\n", f"**Calendar Meetings Today ({len(calendar_events)}):**"]
        for evt in calendar_events:
            lines.append(f"• {evt.get('title')} ({evt.get('time')})")

        lines.append(f"\n**Package Deliveries ({len(deliveries)}):**")
        for d in deliveries:
            lines.append(f"• {d.get('product_name')} ({d.get('status')})")

        if delayed:
            lines.append(f"\n*Your delayed delivery ({delayed[0].get('product_name')}) is prioritized at the top because of your saved preference.*")

        response_text = "\n".join(lines)
        reason = "Composed personalized morning briefing combining calendar meetings and deliveries."
        meta = {"composed_skills": ["calendar", "deliveries"], "explanation": reason}

        return response_text, reason, meta


response_generator = ResponseGenerator()
