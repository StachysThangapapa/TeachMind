"""
TeachMind End-to-End Workflow Verification Script.
Simulates:
1. Vector Search (/skills/search)
2. Task Execution with Initial Skill (v1.0)
3. Skill Verification & Accuracy Scoring
4. Human Correction & Version Increment (v1.1)
5. Re-Verification & Reuse Confirmation
"""

import sys
import json
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.verification.evaluator import SkillEvaluator
from backend.verification.metrics import calculate_accuracy


def mock_skill_search(query: str, top_k: int = 3) -> dict:
    """Simulates Skill Memory vector search endpoint (POST /skills/search)."""
    return {
        "query": query,
        "results": [
            {
                "skill_id": "skill_001",
                "name": "refund_processing",
                "similarity": 0.94,
                "skill": {
                    "description": "Determine whether a customer qualifies for a refund.",
                    "triggers": ["refund request", "return policy"],
                    "steps": [
                        {
                            "step": 1,
                            "instruction": "Evaluate purchase date against 7-day policy."
                        },
                        {
                            "step": 2,
                            "instruction": "Check item status for clearance or damage."
                        }
                    ],
                    "rules": [
                        {
                            "condition": "Purchase date within 7 days",
                            "action": "approve"
                        },
                        {
                            "condition": "Purchase date past 7 days or clearance item",
                            "action": "reject"
                        }
                    ],
                    "examples": []
                }
            }
        ]
    }


def create_agent(skill_version: str = "1.0"):
    """Returns a mock agent runner closure based on the active skill version."""
    def agent_runner(user_input: str) -> dict:
        text = user_input.lower()
        
        # Version 1.1 includes the human correction for damaged items
        if skill_version == "1.1" and "damaged" in text:
            return {
                "decision": "approve",
                "reason": "Approved under exception rule added in v1.1 for damaged items."
            }

        if "3 days" in text or "7 days" in text:
            return {"decision": "approve", "reason": "Purchased within 7-day refund window."}
        
        return {"decision": "reject", "reason": "Exceeds refund policy or clearance item."}

    return agent_runner


def run_demo():
    print("=" * 70)
    print("           TEACHMIND END-TO-END WORKFLOW VERIFICATION           ")
    print("=" * 70)
    
    # Step 1: Simulate Skill Memory Vector Search
    query = "Customer bought headphones 3 days ago. Can they get a refund?"
    search_response = mock_skill_search(query=query)
    print(f"\n[1] POST /skills/search for query: '{query}'")
    print(f"    Matched Skill ID  : {search_response['results'][0]['skill_id']}")
    print(f"    Similarity Score  : {search_response['results'][0]['similarity']}")
    print(f"    Matched Skill Name: {search_response['results'][0]['name']}")

    # Step 2: Load Test Scenario File
    scenario_path = Path(__file__).parent.parent / "tests" / "scenarios" / "refund_processing.json"
    print(f"\n[2] Loading Test Scenario File: {scenario_path.name}")
    
    # Step 3: Evaluate Initial Skill (v1.0)
    print("\n[3] Evaluating Initial Skill (v1.0)...")
    evaluator_v1 = SkillEvaluator(agent_runner=create_agent(skill_version="1.0"))
    report_v1 = evaluator_v1.evaluate_scenario(str(scenario_path))
    
    print(f"    Total Cases: {report_v1['total_cases']}")
    print(f"    Correct    : {report_v1['correct']}")
    print(f"    Incorrect  : {report_v1['incorrect']}")
    print(f"    Accuracy   : {report_v1['accuracy'] * 100:.1f}%")
    
    for r in report_v1["results"]:
        status = "PASSED" if r["passed"] else "FAILED"
        print(f"    - Input: '{r['input']}' | Expected: {r['expected']} | Actual: {r['actual']} [{status}]")

    # Step 4: Simulate Human Correction (v1.1)
    print("\n[4] Simulating Human Correction:")
    print("    User Instruction: 'Damaged products should be approved even if clearance or past 7 days.'")
    print("    Skill Memory updated -> Version bumped: 1.0 -> 1.1")

    # Step 5: Evaluate Updated Skill (v1.1)
    print("\n[5] Evaluating Corrected Skill (v1.1)...")
    evaluator_v2 = SkillEvaluator(agent_runner=create_agent(skill_version="1.1"))
    report_v2 = evaluator_v2.evaluate_scenario(str(scenario_path))
    
    print(f"    Total Cases: {report_v2['total_cases']}")
    print(f"    Correct    : {report_v2['correct']}")
    print(f"    Incorrect  : {report_v2['incorrect']}")
    print(f"    Accuracy   : {report_v2['accuracy'] * 100:.1f}%")

    for r in report_v2["results"]:
        status = "PASSED" if r["passed"] else "FAILED"
        print(f"    - Input: '{r['input']}' | Expected: {r['expected']} | Actual: {r['actual']} [{status}]")

    print("\n" + "=" * 70)
    if report_v2["accuracy"] == 1.0:
        print(" SUCCESS: TEACH -> STORE -> TEST -> VERIFY -> CORRECT -> UPDATE -> REUSE")
        print("          All verification checks completed cleanly.")
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
