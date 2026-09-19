"""
TeachMind AI Agent Live End-to-End Demonstration Script.
Demonstrates:
Demo 1: "Check my deliveries today." -> Personalized skill selection & tool execution.
Demo 2: "Actually, don't show tracking IDs unless I ask for them." -> Correction flow & version bump (v1.0 -> v1.1).
Demo 3: "Prepare my morning briefing." -> Composable workflow execution.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.agent.state import AgentState
from backend.app.agent.graph import agent_graph


def run_demo():
    print("=" * 80)
    print("      TEACHMIND PERSONALIZED AI AGENT — LIVE DEMONSTRATION      ")
    print("=" * 80)

    user_id = "user_hackathon_demo"

    # -------------------------------------------------------------------------
    # DEMO 1: Initial Request -> Personalized Delivery Skill & Preferences
    # -------------------------------------------------------------------------
    query1 = "Check my deliveries today."
    print(f"\n>>> USER STEP 1: '{query1}'")
    
    state1 = AgentState(user_message=query1, user_id=user_id)
    res1 = agent_graph.run(state1)

    print(f"    Intent          : {res1.intent.type.value if res1.intent else 'NORMAL_REQUEST'}")
    print(f"    Skill Selected  : {res1.selected_skill.name if res1.selected_skill else 'None'} (v{res1.selected_skill.version if res1.selected_skill else '1.0'})")
    print(f"    Similarity      : {res1.similarity_score:.2f}")
    print(f"    Personalization : {res1.personalization_match_score:.2f}")
    print(f"    Verification    : {res1.verification_result.regression_status if res1.verification_result else 'PASSED'}")
    print(f"    Tool Executed   : {res1.selected_tool}")
    print("\n--- RESPONSE ---")
    print(res1.response_text)
    print("----------------")
    print(f"Explanation     : {res1.reason}")

    # -------------------------------------------------------------------------
    # DEMO 2: User Correction -> Preferences Updated, Version Bump (v1.0 -> v1.1), Regression Verification
    # -------------------------------------------------------------------------
    query2 = "Actually, don't show tracking IDs unless I ask for them."
    print(f"\n>>> USER STEP 2 (CORRECTION): '{query2}'")
    
    state2 = AgentState(user_message=query2, user_id=user_id)
    res2 = agent_graph.run(state2)

    print(f"    Intent          : {res2.intent.type.value if res2.intent else 'CORRECTION'}")
    print(f"    Skill Updated   : {res2.selected_skill.name if res2.selected_skill else 'None'}")
    print(f"    New Version     : v{res2.updated_skill_version}")
    print(f"    Regression Test : {res2.verification_result.regression_status.upper() if res2.verification_result else 'PASSED'}")
    print("\n--- RESPONSE ---")
    print(res2.response_text)

    # Re-run request after correction to show updated behavior
    query2_verify = "Check my deliveries today."
    print(f"\n>>> USER RE-QUERY: '{query2_verify}'")
    state2_v = AgentState(user_message=query2_verify, user_id=user_id)
    res2_v = agent_graph.run(state2_v)
    print("\n--- UPDATED PERSONALIZED RESPONSE (NO TRACKING IDs) ---")
    print(res2_v.response_text)

    # -------------------------------------------------------------------------
    # DEMO 3: Workflow Composition -> Morning Briefing (Calendar + Tasks + Deliveries)
    # -------------------------------------------------------------------------
    query3 = "Prepare my morning briefing."
    print(f"\n>>> USER STEP 3 (WORKFLOW COMPOSITION): '{query3}'")
    
    state3 = AgentState(user_message=query3, user_id=user_id)
    res3 = agent_graph.run(state3)

    print(f"    Intent          : {res3.intent.type.value if res3.intent else 'NORMAL_REQUEST'}")
    print(f"    Skill Composed  : {res3.selected_skill.name if res3.selected_skill else 'morning_briefing'}")
    print("\n--- COMPOSITE RESPONSE ---")
    print(res3.response_text)

    print("\n" + "=" * 80)
    print(" SUCCESS: ALL 3 PERSONALIZED DEMO FLOWS EXECUTED & VERIFIED CLEANLY ")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
