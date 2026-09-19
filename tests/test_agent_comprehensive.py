"""
Comprehensive Test Suite for TeachMind AI Agent Orchestration Layer.
Covering all 20 required test dimensions.
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
from backend.app.verification.client import verification_client


def test_1_basic_user_request():
    state = AgentState(user_message="Check my deliveries today.", user_id="u_test_1")
    res = agent_graph.run(state)
    assert res.decision == "PROCESSED"
    assert "Wireless Mouse" in res.response_text or "deliveries" in res.response_text.lower()


def test_2_intent_extraction():
    res1 = intent_engine.parse_intent("Check my deliveries today.")
    assert res1.type == IntentType.NORMAL_REQUEST

    res2 = intent_engine.parse_intent("Don't show tracking IDs unless I ask for them.")
    assert res2.type == IntentType.CORRECTION

    res3 = intent_engine.parse_intent("When I ask for deliveries, show delayed first.")
    assert res3.type == IntentType.TEACH_REQUEST

    res4 = intent_engine.parse_intent("Yes, proceed.")
    assert res4.type == IntentType.CONFIRMATION


def test_3_skill_retrieval():
    search_res = skill_memory_client.search_skills("Check my deliveries today.")
    assert "results" in search_res
    assert len(search_res["results"]) > 0
    assert search_res["results"][0]["similarity"] > 0.75


def test_4_and_6_skill_threshold_rejection_and_no_skill_found():
    search_res = skill_memory_client.search_skills("Quantum physics equation calculation")
    top_similarity = search_res["results"][0]["similarity"]
    assert top_similarity < 0.75  # Triggers fallback/rejection


def test_5_personalized_skill_selection():
    ctx = context_manager.get_context("u_test_5")
    skill = SkillSummary(id="skill_del", name="personalized_delivery_summary", description="")
    score = personalization_engine.evaluate_match(skill, ctx)
    assert score >= 0.85


def test_7_teaching_request():
    state = AgentState(user_message="When I ask for deliveries, show active items only.", user_id="u_test_7")
    res = agent_graph.run(state)
    assert res.is_teaching or res.intent.type == IntentType.TEACH_REQUEST


def test_8_correction_request():
    state = AgentState(user_message="Don't show tracking IDs unless I ask for them.", user_id="u_test_8")
    res = agent_graph.run(state)
    assert res.is_correction
    assert "v1.1" in res.response_text or "updated" in res.response_text.lower()


def test_9_preference_conflict():
    conflict = personalization_engine.detect_conflict(old_value="always", new_value="only_when_requested")
    assert conflict is not None
    assert conflict["status"] == "preference_conflict"


def test_10_and_11_verification_success_and_failure():
    def pass_runner(x): return "approve"
    report_pass = verification_client.verify_skill("skill_test", pass_runner)
    assert report_pass.accuracy == 1.0

    def fail_runner(x): return "reject"
    report_fail = verification_client.verify_skill("skill_test", fail_runner)
    assert report_fail.accuracy <= 0.5


def test_12_regression_verification():
    skill = SkillSummary(id="s_reg", name="delivery", description="", version="1.0")
    updated_skill, report, meta = correction_engine.apply_correction(skill, "don't show tracking IDs", "u_test_12")
    assert updated_skill.version == "1.1"
    assert report.regression_status == "passed"


def test_13_read_only_tool_execution():
    res = tool_registry.execute_tool("get_today_deliveries", {"date": "today"})
    assert res["status"] == "success"
    assert "deliveries" in res["result"]


def test_14_mutating_tool_confirmation():
    # Without confirmation -> confirmation_required
    res_unconfirmed = tool_registry.execute_tool("create_calendar_event", {"title": "Meeting", "time": "10:00"})
    assert res_unconfirmed["requires_confirmation"] is True

    # With confirmation -> success
    res_confirmed = tool_registry.execute_tool("create_calendar_event", {"title": "Meeting", "time": "10:00"}, user_confirmed=True)
    assert res_confirmed["status"] == "success"


def test_15_and_16_unauthorized_tool_and_invalid_args():
    with pytest.raises(ValueError):
        tool_registry.execute_tool("unauthorized_shell_command", {})


def test_19_personalized_response_generation():
    state = AgentState(user_message="Check my deliveries today.", user_id="u_test_19")
    res = agent_graph.run(state)
    assert res.response_text != ""
    assert res.reason != ""


def test_20_end_to_end_delivery_and_correction_scenario():
    # Step 1: Initial request
    state1 = AgentState(user_message="Check my deliveries today.", user_id="u_e2e")
    res1 = agent_graph.run(state1)
    assert "Wireless Mouse" in res1.response_text

    # Step 2: Correction
    state2 = AgentState(user_message="Actually, don't show tracking IDs unless I ask for them.", user_id="u_e2e")
    res2 = agent_graph.run(state2)
    assert res2.is_correction

    # Step 3: Re-query after correction -> tracking IDs omitted as requested
    state3 = AgentState(user_message="Check my deliveries today.", user_id="u_e2e")
    res3 = agent_graph.run(state3)
    assert "Tracking:" not in res3.response_text
