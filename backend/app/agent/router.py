"""
Router Logic for TeachMind LangGraph Execution Graph.
"""

from typing import Literal
from backend.app.agent.state import AgentState


def route_intent(state: AgentState) -> Literal["process_correction", "retrieve_skills"]:
    """Routes based on intent classification."""
    if state.is_correction:
        return "process_correction"
    return "retrieve_skills"


def route_verification(state: AgentState) -> Literal["execute_tool", "handle_failure"]:
    """Routes based on verification status."""
    if state.verification_result and state.verification_result.accuracy < 0.5:
        return "handle_failure"
    return "execute_tool"
