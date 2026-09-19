"""
Automated unit tests for TeachMind Verification Framework & Skill Schema Contracts.
"""

import pytest
from pathlib import Path
from backend.verification.metrics import calculate_accuracy
from backend.verification.evaluator import SkillEvaluator
from backend.verification.test_cases import TestCaseLoader


def test_calculate_accuracy_normal():
    assert calculate_accuracy(4, 5) == 0.8
    assert calculate_accuracy(5, 5) == 1.0
    assert calculate_accuracy(0, 5) == 0.0


def test_calculate_accuracy_zero_cases():
    assert calculate_accuracy(0, 0) == 0.0


def test_calculate_accuracy_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_accuracy(-1, 5)
    with pytest.raises(ValueError):
        calculate_accuracy(6, 5)


def test_skill_search_response_schema():
    """Verify that vector search results match teammate response schema."""
    search_response = {
        "query": "Customer refund request",
        "results": [
            {
                "skill_id": "skill_001",
                "name": "refund_processing",
                "similarity": 0.91,
                "skill": {
                    "description": "Determine whether a customer qualifies for a refund.",
                    "triggers": ["refund request"],
                    "steps": [{"step": 1, "instruction": "Check date."}],
                    "rules": [{"condition": "Within 7 days", "action": "approve"}],
                    "examples": []
                }
            }
        ]
    }

    assert "query" in search_response
    assert "results" in search_response
    res = search_response["results"][0]
    assert res["skill_id"] == "skill_001"
    assert "similarity" in res
    assert "steps" in res["skill"]
    assert "rules" in res["skill"]
    assert res["skill"]["steps"][0]["step"] == 1


def test_evaluator_mock_agent_all_pass():
    def mock_agent(user_input: str):
        if "damaged" in user_input.lower() or "3 days" in user_input.lower():
            return {"decision": "approve", "reason": "Valid refund case"}
        return {"decision": "reject", "reason": "Exceeds refund policy"}

    scenario = {
        "skill": "refund_processing",
        "cases": [
            {"input": "Product purchased 3 days ago.", "expected": "approve"},
            {"input": "Normal product purchased 15 days ago.", "expected": "reject"},
            {"input": "Damaged product arrived.", "expected": "approve"}
        ]
    }

    evaluator = SkillEvaluator(agent_runner=mock_agent)
    report = evaluator.evaluate_scenario(scenario)

    assert report["skill_id"] == "refund_processing"
    assert report["total_cases"] == 3
    assert report["correct"] == 3
    assert report["incorrect"] == 0
    assert report["accuracy"] == 1.0
    assert len(report["results"]) == 3
    assert report["results"][0]["passed"] is True


def test_evaluator_mock_agent_partial_failure():
    def mock_agent(user_input: str):
        return "approve"

    scenario = {
        "skill": "refund_processing",
        "cases": [
            {"input": "Product purchased 3 days ago.", "expected": "approve"},
            {"input": "Normal product purchased 15 days ago.", "expected": "reject"}
        ]
    }

    evaluator = SkillEvaluator(agent_runner=mock_agent)
    report = evaluator.evaluate_scenario(scenario)

    assert report["total_cases"] == 2
    assert report["correct"] == 1
    assert report["incorrect"] == 1
    assert report["accuracy"] == 0.5


def test_evaluator_scenario_file_loading():
    scenario_file = Path(__file__).parent / "scenarios" / "refund_processing.json"
    assert scenario_file.exists()

    def mock_agent(user_input: str):
        if "3 days" in user_input or "7 days" in user_input:
            return "approve"
        if "damaged" in user_input:
            return "approve"
        return "reject"

    evaluator = SkillEvaluator(agent_runner=mock_agent)
    report = evaluator.evaluate_scenario(str(scenario_file))

    assert report["skill_id"] == "refund_processing"
    assert report["total_cases"] == 5
    assert report["accuracy"] == 1.0
