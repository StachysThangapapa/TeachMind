"""
Pydantic Schemas for TeachMind AI Agent.
Defines intent types, state payloads, API requests, and response models.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    NORMAL_REQUEST = "NORMAL_REQUEST"
    TEACH_REQUEST = "TEACH_REQUEST"
    CORRECTION = "CORRECTION"
    CLARIFICATION = "CLARIFICATION"
    CONFIRMATION = "CONFIRMATION"
    CANCELLATION = "CANCELLATION"


class ParsedIntent(BaseModel):
    type: IntentType = IntentType.NORMAL_REQUEST
    intent: str = "general_query"
    entities: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.90


class ExecutionTimelineStage(str, Enum):
    IDLE = "idle"
    LOAD_CONTEXT = "load_context"
    UNDERSTAND_INTENT = "understand_intent"
    SEARCHING_MEMORY = "searching_memory"
    FOUND_SKILL = "found_skill"
    APPLYING_RULES = "applying_rules"
    VERIFYING = "verifying"
    EXECUTING_TOOL = "executing_tool"
    COMPLETE = "complete"
    ERROR = "error"


class ExecutionTimelineStep(BaseModel):
    stage: str
    label: str
    status: str = "completed"  # "pending" | "active" | "completed" | "skipped" | "failed"
    detail: Optional[str] = None
    timestamp: Optional[str] = None


class PersonalPreferences(BaseModel):
    delivery: Dict[str, Any] = Field(
        default_factory=lambda: {
            "show_active_only": True,
            "prioritize_delayed": True,
            "show_expected_date": True,
            "show_tracking_id": "only_if_delayed"  # "always", "only_if_delayed", "only_when_requested"
        }
    )
    briefing: Dict[str, Any] = Field(
        default_factory=lambda: {
            "include_calendar": True,
            "include_tasks": True,
            "include_deliveries": True
        }
    )


class Permissions(BaseModel):
    read_calendar: str = "automatic"
    read_deliveries: str = "automatic"
    create_calendar_event: str = "confirmation_required"
    delete_calendar_event: str = "explicit_confirmation"
    purchase_product: str = "never_automatic"


class PersonalContext(BaseModel):
    user_id: str = "user_default"
    preferences: PersonalPreferences = Field(default_factory=PersonalPreferences)
    permissions: Permissions = Field(default_factory=Permissions)
    constraints: List[str] = Field(default_factory=list)
    correction_history: List[Dict[str, Any]] = Field(default_factory=list)


class SkillSummary(BaseModel):
    id: str = "skill_001"
    name: str = "generic_skill"
    description: str = ""
    version: str = "1.0"
    confidence: float = 0.90
    triggers: List[str] = Field(default_factory=list)
    steps: List[Dict[str, Any]] = Field(default_factory=list)
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    exceptions: List[Dict[str, Any]] = Field(default_factory=list)


class VerificationReport(BaseModel):
    skill_id: str = "skill_001"
    total_cases: int = 5
    correct: int = 5
    incorrect: int = 0
    accuracy: float = 1.0
    skill_confidence: float = 0.90
    personalized_reliability: float = 0.95
    regression_status: str = "passed"
    results: List[Dict[str, Any]] = Field(default_factory=list)


class TaskExecutionRequest(BaseModel):
    query: str
    user_id: str = "user_default"
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    skill_id_override: Optional[str] = None


class TaskExecutionResponse(BaseModel):
    status: str = "success"
    message: str = ""
    decision: Optional[str] = "PROCESSED"
    reason: str = ""
    intent: Optional[ParsedIntent] = None
    skill_used: Optional[SkillSummary] = None
    similarity: float = 0.0
    confidence: float = 0.90
    personalization: Dict[str, Any] = Field(default_factory=dict)
    verification: Optional[VerificationReport] = None
    tool_executed: Optional[str] = None
    requires_confirmation: bool = False
    action_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    execution_trace: List[str] = Field(default_factory=list)
    timeline: List[ExecutionTimelineStep] = Field(default_factory=list)


class ConfirmActionRequest(BaseModel):
    action_id: str
    confirmed: bool = True
    user_id: str = "user_default"


class ConfirmActionResponse(BaseModel):
    status: str
    message: str
    action_id: str
    data: Optional[Dict[str, Any]] = None
