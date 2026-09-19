"""
Skill Evaluator Module for TeachMind Verification Framework.
Runs test scenarios against agent interfaces and produces detailed validation reports.
"""

from typing import Callable, Dict, Any, List, Union
from backend.verification.metrics import calculate_accuracy
from backend.verification.test_cases import TestCaseLoader


class SkillEvaluator:
    """
    Evaluates an agent's performance against defined test scenarios.
    Uses dependency injection for the agent execution callable.
    """

    def __init__(self, agent_runner: Callable[[str], Union[str, Dict[str, Any]]]):
        """
        Initialize the evaluator.

        :param agent_runner: A callable accepting input text string and returning
                             either a decision string (e.g. 'approve') or a dict
                             containing a 'decision' key.
        """
        self.agent_runner = agent_runner

    def evaluate_scenario(
        self,
        scenario: Union[Dict[str, Any], str],
        skill_id: str = "skill_001"
    ) -> Dict[str, Any]:
        """
        Run all test cases in a scenario through the agent runner and generate a report.

        :param scenario: A scenario dictionary or file path to JSON.
        :param skill_id: ID of the skill being evaluated.
        :return: Structured validation report dictionary.
        """
        if isinstance(scenario, (str, bytes)):
            scenario_data = TestCaseLoader.load_from_file(scenario)
        else:
            scenario_data = TestCaseLoader.load_from_dict(scenario)

        target_skill_id = scenario_data.get("skill", skill_id)
        cases: List[Dict[str, Any]] = scenario_data.get("cases", [])

        correct = 0
        results = []

        for case in cases:
            case_input = case.get("input", "")
            expected = str(case.get("expected", "")).strip().lower()

            try:
                raw_response = self.agent_runner(case_input)
                if isinstance(raw_response, dict):
                    actual = str(raw_response.get("decision", "")).strip().lower()
                    reason = raw_response.get("reason", "")
                else:
                    actual = str(raw_response).strip().lower()
                    reason = ""
            except Exception as e:
                actual = "error"
                reason = str(e)

            passed = (actual == expected)
            if passed:
                correct += 1

            results.append({
                "input": case_input,
                "expected": expected,
                "actual": actual,
                "passed": passed,
                "reason": reason
            })

        total = len(cases)
        accuracy = calculate_accuracy(correct, total)

        return {
            "skill_id": target_skill_id,
            "total_cases": total,
            "correct": correct,
            "incorrect": total - correct,
            "accuracy": accuracy,
            "results": results
        }
