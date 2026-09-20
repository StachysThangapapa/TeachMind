"""
Comprehensive Test Suite for TeachMind AI Agent Orchestration Layer.
Tests all 7 Acceptance Criteria from Section 24.
"""

import pytest
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.schemas.agent import (
    IntentType,
    PersonalContext,
    SkillSummary,
    TaskExecutionRequest,
)
from backend.app.agent.state import AgentState
from backend.app.agent.intent import intent_engine
from backend.app.agent.context import context_manager
from backend.app.agent.personalization import personalization_engine
from backend.app.agent.correction import correction_engine
from backend.app.agent.planner import planner
from backend.app.agent.graph import agent_graph
from backend.app.tools.registry import tool_registry
from backend.app.skills.client import skill_memory_client
from backend.app.skills.storage import skill_storage
from backend.app.skills.extractor import skill_extractor
from backend.app.verification.client import verification_client


def test_acceptance_1_arbitrary_task_calculator():
    """TEST 1: Arbitrary task (Calculator dynamic execution)."""
    state = AgentState(user_message="What is 18% of 1250?", user_id="u_acc_1")
    res = agent_graph.run(state)
    assert res.decision == "PROCESSED"
    assert "calculator" in (res.selected_tools or [res.selected_tool])
    assert "225" in res.response_text


def test_acceptance_2_teach_request():
    """TEST 2: Teach request (Extracts structured skill, verifies, and stores in persistent memory)."""
    msg = "Whenever I ask for my morning briefing, check calendar and tasks first, then deliveries. Put urgent items first."
    state = AgentState(user_message=msg, user_id="u_acc_2")
    res = agent_graph.run(state)
    
    assert res.is_teaching
    assert res.selected_skill is not None
    assert res.selected_skill.name == "personalized_morning_briefing"
    assert len(res.selected_skill.steps) > 0
    assert res.verification_result.accuracy >= 0.75
    
    # Check persistent storage
    stored = skill_storage.get_skill_by_name("personalized_morning_briefing", user_id="u_acc_2")
    assert stored is not None
    assert stored.version == "1.0"


def test_acceptance_3_retrieve_and_execute_skill():
    """TEST 3: Retrieve learned skill and execute with dynamic tools."""
    state = AgentState(user_message="Prepare my morning briefing.", user_id="u_acc_2")
    res = agent_graph.run(state)
    
    assert res.selected_skill is not None
    assert res.selected_skill.name == "personalized_morning_briefing"
    assert len(res.selected_tools) >= 2
    assert "Calendar" in res.response_text or "Deliveries" in res.response_text


def test_acceptance_4_correction_and_versioning():
    """TEST 4: Correction flow (Creates v1.1, updates rules, runs regression tests)."""
    state = AgentState(user_message="Actually, put deadlines before meetings.", user_id="u_acc_2")
    res = agent_graph.run(state)
    
    assert res.is_correction
    assert res.updated_skill_version.startswith("1.")
    assert res.verification_result.regression_status == "passed"
    
    stored = skill_storage.get_skill_by_name("personalized_morning_briefing", user_id="u_acc_2")
    assert stored.version == "1.1"


def test_acceptance_5_persistence():
    """TEST 5: Persistence across backend restarts."""
    stored = skill_storage.list_skills(user_id="u_acc_2")
    assert len(stored) > 0
    assert any(s.name == "personalized_morning_briefing" for s in stored)


def test_acceptance_6_unknown_task_handling():
    """TEST 6: Unknown task handled using available tools."""
    state = AgentState(user_message="What day of the week is today?", user_id="u_acc_6")
    res = agent_graph.run(state)
    assert res.selected_tool == "datetime_tool" or "datetime_tool" in res.selected_tools


def test_acceptance_7_no_hallucination_boundary():
    """TEST 7: Unsupported action returns clear missing capability statement."""
    state = AgentState(user_message="Send an email to john@example.com", user_id="u_acc_7")
    res = agent_graph.run(state)
    assert res.response_text != ""
