"""
LangGraph State Graph Assembly for TeachMind AI Agent.
Constructs and compiles the agent execution pipeline.
"""

from typing import Dict, Any
from backend.app.agent.state import AgentState
from backend.app.agent.nodes import (
    load_context_node,
    understand_intent_node,
    retrieve_skills_node,
    select_personalized_skill_node,
    plan_node,
    verify_node,
    execute_tool_node,
    process_correction_node,
    generate_response_node,
)
from backend.app.agent.router import route_intent, route_verification


class AgentStateGraph:
    """State graph orchestrating the agent execution lifecycle."""

    def run(self, initial_state: AgentState) -> AgentState:
        """
        Executes the agent state graph sequentially with dynamic routing.
        """
        state_dict = initial_state.model_dump()

        # Step 1: Load Context
        state_dict.update(load_context_node(AgentState(**state_dict)))
        
        # Step 2: Understand Intent
        state_dict.update(understand_intent_node(AgentState(**state_dict)))
        current_state = AgentState(**state_dict)

        # Check Routing for Correction
        if route_intent(current_state) == "process_correction":
            # Direct route to correction flow
            state_dict.update(process_correction_node(current_state))
            return AgentState(**state_dict)

        # Step 3: Retrieve Skills
        state_dict.update(retrieve_skills_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 4: Select Personalized Skill
        state_dict.update(select_personalized_skill_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 5: Plan Execution
        state_dict.update(plan_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 6: Verify Skill
        state_dict.update(verify_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 7: Execute Tool
        state_dict.update(execute_tool_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 8: Generate Explainable Response
        state_dict.update(generate_response_node(current_state))
        return AgentState(**state_dict)


agent_graph = AgentStateGraph()
