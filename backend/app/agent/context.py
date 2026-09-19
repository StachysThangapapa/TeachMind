"""
Personal Context Manager for TeachMind AI Agent.
Manages user preferences, constraints, correction history, and permission boundaries.
"""

from typing import Dict, Any, Optional
from backend.app.schemas.agent import PersonalContext, PersonalPreferences, Permissions


class PersonalContextManager:
    """Manages reading and updating persistent personal context for users."""

    def __init__(self):
        # In-memory user context store (can be connected to PostgreSQL)
        self._contexts: Dict[str, PersonalContext] = {}

    def get_context(self, user_id: str = "user_default") -> PersonalContext:
        """Fetch or initialize personal context for a user."""
        if user_id not in self._contexts:
            self._contexts[user_id] = PersonalContext(user_id=user_id)
        return self._contexts[user_id]

    def update_preference(self, user_id: str, domain: str, key: str, value: Any) -> PersonalContext:
        """Update a user preference entry."""
        ctx = self.get_context(user_id)
        domain_dict = getattr(ctx.preferences, domain, {})
        domain_dict[key] = value
        setattr(ctx.preferences, domain, domain_dict)
        return ctx

    def record_correction(self, user_id: str, correction: str, target: str) -> PersonalContext:
        """Record user correction entry in history."""
        ctx = self.get_context(user_id)
        ctx.correction_history.append({
            "correction": correction,
            "target": target
        })
        return ctx


context_manager = PersonalContextManager()
