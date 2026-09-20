"""
LangGraph State Graph Assembly for TeachMind AI Agent.
Constructs and compiles the agent execution pipeline.
"""

from typing import Dict, Any
from backend.app.agent.state import AgentState
from backend.app.agent.nodes import (
    load_context_node,
    understand_intent_node,
    extract_skill_node,
    retrieve_skills_node,
    rerank_skills_node,
    plan_node,
    verify_node,
    execute_tools_node,
    process_correction_node,
    generate_response_node,
)
from backend.app.agent.router import route_intent, route_verification


class AgentStateGraph:
    """State graph orchestrating the agent execution lifecycle."""

    def run(self, initial_state: AgentState) -> AgentState:
        """
        Executes the agent state graph with conditional routing.
        """
        state_dict = initial_state.model_dump()

        # Step 1: Load Context
        state_dict.update(load_context_node(AgentState(**state_dict)))
        
        # Step 2: Understand Intent
        state_dict.update(understand_intent_node(AgentState(**state_dict)))
        current_state = AgentState(**state_dict)

        # Route A: Teaching Flow
        if current_state.is_teaching:
            state_dict.update(extract_skill_node(current_state))
            return AgentState(**state_dict)

        # Route B: Correction Flow
        if current_state.is_correction or route_intent(current_state) == "process_correction":
            state_dict.update(process_correction_node(current_state))
            return AgentState(**state_dict)

        # Route C: Normal Task Flow
        # Step 3: Retrieve Skills
        state_dict.update(retrieve_skills_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 4: Rerank Skills
        state_dict.update(rerank_skills_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 5: Dynamic Planning & Tool Selection
        state_dict.update(plan_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 6: Verify Skill
        state_dict.update(verify_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 7: Execute Dynamic Tools
        state_dict.update(execute_tools_node(current_state))
        current_state = AgentState(**state_dict)

        # Step 8: Generate Explainable Response
        state_dict.update(generate_response_node(current_state))
        return AgentState(**state_dict)


agent_graph = AgentStateGraph()
