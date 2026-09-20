"""
Typed Agent State Definition for TeachMind LangGraph Execution Graph.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.agent import (
    ParsedIntent,
    PersonalContext,
    SkillSummary,
    VerificationReport,
    ExecutionTimelineStep,
)


class AgentState(BaseModel):
    """Strongly-typed state container passed across LangGraph nodes."""

    conversation_id: str = "conv_default"
    user_id: str = "user_default"
    user_message: str = ""
    
    # Context & Intent
    personal_context: PersonalContext = Field(default_factory=PersonalContext)
    intent: Optional[ParsedIntent] = None
    
    # Skill Memory & Selection
    candidate_skills: List[Dict[str, Any]] = Field(default_factory=list)
    selected_skill: Optional[SkillSummary] = None
    similarity_score: float = 0.0
    personalization_match_score: float = 0.0
    
    # Workflow Planning & Verification
    plan: List[str] = Field(default_factory=list)
    verification_result: Optional[VerificationReport] = None
    
    # Tool Execution & Permissions
    selected_tool: Optional[str] = None
    selected_tools: List[str] = Field(default_factory=list)
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    tool_result: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    action_id: Optional[str] = None
    
    # Correction & Learning State
    is_correction: bool = False
    is_teaching: bool = False
    preference_conflict: Optional[Dict[str, Any]] = None
    updated_skill_version: Optional[str] = None
    
    # Final Output
    decision: str = "PROCESSED"
    reason: str = ""
    response_text: str = ""
    execution_trace: List[str] = Field(default_factory=list)
    timeline: List[ExecutionTimelineStep] = Field(default_factory=list)
    error: Optional[str] = None
