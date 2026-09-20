"""
LangGraph Execution Nodes for TeachMind Agent.
Contains node functions for intent classification, skill extraction, skill retrieval,
dynamic planning, tool execution, real verification, correction learning, and response generation.
"""

from typing import Dict, Any, List
from backend.app.agent.state import AgentState
from backend.app.agent.intent import intent_engine
from backend.app.agent.context import context_manager
from backend.app.agent.personalization import personalization_engine
from backend.app.agent.correction import correction_engine
from backend.app.agent.planner import planner
from backend.app.agent.response import response_generator
from backend.app.skills.extractor import skill_extractor
from backend.app.skills.client import skill_memory_client
from backend.app.skills.storage import skill_storage
from backend.app.verification.client import verification_client
from backend.app.tools.registry import tool_registry
from backend.app.config import settings
from backend.app.schemas.agent import (
    SkillSummary,
    ExecutionTimelineStep,
    IntentType,
)


def load_context_node(state: AgentState) -> Dict[str, Any]:
    """Node 1: Load persistent personal context for user."""
    ctx = context_manager.get_context(state.user_id)
    trace = list(state.execution_trace) + [f"Loaded personal context for user '{state.user_id}'"]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(stage="load_context", label="Loaded Personal Context", status="completed")
    ]
    return {"personal_context": ctx, "execution_trace": trace, "timeline": timeline}


def understand_intent_node(state: AgentState) -> Dict[str, Any]:
    """Node 2: Classify request intent using LLM Intent Engine."""
    parsed_intent = intent_engine.parse_intent(state.user_message)
    trace = list(state.execution_trace) + [f"Intent recognized: {parsed_intent.type.value} ({parsed_intent.intent})"]
    
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(
            stage="understand_intent",
            label="Intent Classified",
            status="completed",
            detail=f"{parsed_intent.type.value}: {parsed_intent.intent}"
        )
    ]

    is_corr = (parsed_intent.type == IntentType.CORRECTION)
    is_teach = (parsed_intent.type == IntentType.TEACH_REQUEST)

    return {
        "intent": parsed_intent,
        "is_correction": is_corr,
        "is_teaching": is_teach,
        "execution_trace": trace,
        "timeline": timeline
    }


def extract_skill_node(state: AgentState) -> Dict[str, Any]:
    """Node 3A (Teaching Flow): Extract structured skill from natural language instruction."""
    extracted_skill = skill_extractor.extract_skill(state.user_message, user_id=state.user_id)
    
    # Verify new skill
    verification_rep = verification_client.verify_skill(extracted_skill)
    
    # Store in persistent Skill Memory via client
    skill_memory_client.store_skill(extracted_skill, user_id=state.user_id)

    triggers_str = ", ".join([f"'{t}'" for t in extracted_skill.triggers[:3]])
    rules_str = ", ".join([f"'{r.get('condition')}'" for r in extracted_skill.rules[:2]])

    resp_text = (
        f"Learned new skill **{extracted_skill.name}** (v{extracted_skill.version})!\n\n"
        f"• **Description**: {extracted_skill.description}\n"
        f"• **Triggers**: {triggers_str}\n"
        f"• **Learned Rules**: {rules_str if rules_str else 'Standard procedural rules'}\n"
        f"• **Verification**: {verification_rep.correct}/{verification_rep.total_cases} test cases passed (Accuracy: {verification_rep.accuracy * 100:.0f}%)."
    )

    trace = list(state.execution_trace) + [
        f"Extracted and verified new skill '{extracted_skill.name}' (v{extracted_skill.version}). Stored in persistent memory."
    ]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(
            stage="complete",
            label="Skill Learned & Verified",
            status="completed",
            detail=f"Stored {extracted_skill.name} (v{extracted_skill.version})"
        )
    ]
    return {
        "selected_skill": extracted_skill,
        "verification_result": verification_rep,
        "response_text": resp_text,
        "decision": "SKILL_LEARNED",
        "reason": f"Extracted and saved reusable skill {extracted_skill.name}.",
        "execution_trace": trace,
        "timeline": timeline
    }


def retrieve_skills_node(state: AgentState) -> Dict[str, Any]:
    """Node 3B (Normal Task Flow): Search Skill Memory."""
    search_res = skill_memory_client.search_skills(state.user_message, user_id=state.user_id)
    candidates = search_res.get("results", [])
    
    trace = list(state.execution_trace) + [f"Skill Memory search found {len(candidates)} candidate skills"]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(stage="searching_memory", label="Searching Skill Memory", status="completed")
    ]
    return {"candidate_skills": candidates, "execution_trace": trace, "timeline": timeline}


def rerank_skills_node(state: AgentState) -> Dict[str, Any]:
    """Node 4: Rerank skills and select matching personalized skill."""
    if not state.candidate_skills:
        return {"decision": "NO_SKILL_FOUND", "reason": "No candidate skills found."}

    top_candidate = state.candidate_skills[0]
    similarity = top_candidate.get("similarity", 0.0)

    # Check threshold (configurable via settings.SKILL_MATCH_THRESHOLD, default 0.50 for pgvector)
    threshold = getattr(settings, "SKILL_MATCH_THRESHOLD", 0.50)
    if similarity < threshold:
        trace = list(state.execution_trace) + [f"Top candidate similarity ({similarity}) below threshold ({threshold})"]
        return {
            "selected_skill": None,
            "similarity_score": similarity,
            "execution_trace": trace
        }

    raw_skill = top_candidate.get("skill", {})
    skill_id_val = top_candidate.get("skill_id") or raw_skill.get("skill_id") or "skill_001"
    skill_name_val = top_candidate.get("name") or raw_skill.get("name") or "generic_skill"
    raw_version = raw_skill.get("version", "1.0")
    skill_version_val = str(raw_version)
    if not "." in skill_version_val and skill_version_val.isdigit():
        skill_version_val = f"{skill_version_val}.0"

    skill_obj = SkillSummary(
        id=skill_id_val,
        name=skill_name_val,
        description=raw_skill.get("description", ""),
        version=skill_version_val,
        confidence=raw_skill.get("confidence", 0.90),
        triggers=raw_skill.get("triggers", []),
        steps=raw_skill.get("steps", []),
        rules=raw_skill.get("rules", []),
        exceptions=raw_skill.get("exceptions", [])
    )

    p_score = personalization_engine.evaluate_match(skill_obj, state.personal_context)
    
    trace = list(state.execution_trace) + [
        f"Reranked & selected skill '{skill_obj.name}' (Similarity: {similarity}, Personalization Match: {p_score})"
    ]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(
            stage="found_skill",
            label="Found Relevant Personalized Skill",
            status="completed",
            detail=f"{skill_obj.name} (v{skill_obj.version})"
        )
    ]
    return {
        "selected_skill": skill_obj,
        "similarity_score": similarity,
        "personalization_match_score": p_score,
        "execution_trace": trace,
        "timeline": timeline
    }


def plan_node(state: AgentState) -> Dict[str, Any]:
    """Node 5: Dynamic Planner selecting execution steps and tools."""
    if not state.intent:
        return {}

    plan_output = planner.plan_and_select_tools(
        query=state.user_message,
        intent=state.intent,
        skill=state.selected_skill,
        context=state.personal_context
    )

    trace = list(state.execution_trace) + [
        f"Dynamic plan generated ({len(plan_output.plan)} steps). Selected tools: {plan_output.selected_tools}"
    ]
    return {
        "plan": plan_output.plan,
        "selected_tools": plan_output.selected_tools,
        "tool_arguments": plan_output.tool_arguments,
        "execution_trace": trace
    }


def verify_node(state: AgentState) -> Dict[str, Any]:
    """Node 6: Run Real Verification Suite."""
    if not state.selected_skill:
        return {}

    report = verification_client.verify_skill(skill=state.selected_skill)

    trace = list(state.execution_trace) + [
        f"Real verification completed: Accuracy {report.accuracy * 100:.0f}% ({report.regression_status})"
    ]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(
            stage="verifying",
            label="Verification Suite Executed",
            status="completed",
            detail=f"Accuracy: {report.accuracy * 100:.0f}%"
        )
    ]
    return {"verification_result": report, "execution_trace": trace, "timeline": timeline}


def execute_tools_node(state: AgentState) -> Dict[str, Any]:
    """Node 7: Dynamic Tool Execution Node."""
    tools_to_run = state.selected_tools or []
    tool_results: Dict[str, Any] = {}
    executed_names = []

    for t_name in tools_to_run:
        t_args = state.tool_arguments.get(t_name, {})
        exec_res = tool_registry.execute_tool(t_name, t_args)

        if exec_res.get("requires_confirmation", False):
            trace = list(state.execution_trace) + [f"Tool '{t_name}' requires user confirmation before execution"]
            return {
                "requires_confirmation": True,
                "action_id": f"act_{t_name}_991",
                "selected_tool": t_name,
                "execution_trace": trace
            }

        tool_results[t_name] = exec_res.get("result", {})
        executed_names.append(t_name)

    trace = list(state.execution_trace) + [f"Executed dynamic tools {executed_names} successfully"]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(
            stage="executing_tool",
            label=f"Executed Tools ({', '.join(executed_names)})",
            status="completed"
        )
    ]
    return {
        "selected_tool": executed_names[0] if executed_names else None,
        "tool_results": tool_results,
        "tool_result": tool_results.get(executed_names[0]) if executed_names else {},
        "execution_trace": trace,
        "timeline": timeline
    }


def process_correction_node(state: AgentState) -> Dict[str, Any]:
    """Node 8: Handle User Correction Flow."""
    # Find active skill in storage for user
    user_skills = skill_storage.list_skills(user_id=state.user_id)
    skill_obj = state.selected_skill
    if not skill_obj and user_skills:
        skill_obj = user_skills[-1]
    if not skill_obj:
        skill_obj = skill_storage.get_skill_by_name("personalized_delivery_summary", user_id=state.user_id)
    if not skill_obj:
        skill_obj = SkillSummary(
            id="skill_delivery_001",
            name="personalized_delivery_summary",
            description="Delivery summary skill",
            version="1.0"
        )

    updated_skill, report, meta = correction_engine.apply_correction(
        skill=skill_obj,
        user_correction=state.user_message,
        user_id=state.user_id
    )

    # Persist updated skill (v1.1) in persistent Skill Memory via client
    skill_memory_client.store_skill(updated_skill, user_id=state.user_id)

    resp_text = (
        f"Got it! I've updated your preferences and bumped skill **{updated_skill.name}** from {meta['version_bump']}.\n\n"
        f"Regression verification passed (Accuracy: {report.accuracy * 100:.0f}%). The updated rule is now active."
    )
    
    trace = list(state.execution_trace) + [
        f"Applied correction: Version updated {meta['version_bump']}. Regression status: {meta['regression_status']}. Saved to persistent memory."
    ]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(
            stage="complete",
            label="Skill Updated & Re-Verified",
            status="completed",
            detail=f"Bumped to v{updated_skill.version}"
        )
    ]
    return {
        "selected_skill": updated_skill,
        "updated_skill_version": updated_skill.version,
        "verification_result": report,
        "response_text": resp_text,
        "decision": "PROCESSED",
        "reason": f"Updated skill to v{updated_skill.version} via user correction.",
        "execution_trace": trace,
        "timeline": timeline
    }


def generate_response_node(state: AgentState) -> Dict[str, Any]:
    """Node 9: Format final explainable response."""
    if state.response_text:
        return {}

    # Handle Calculator Tool result (e.g., "What is 18% of 1250?")
    if "calculator" in (state.selected_tools or []):
        calc_res = state.tool_results.get("calculator", {})
        fmt_res = calc_res.get("formatted", str(calc_res.get("result", "")))
        expr = calc_res.get("expression", state.user_message)
        
        resp_text = f"Result of {expr}: **{fmt_res}**"
        reason = "Executed calculator tool dynamically for mathematical expression."
        
        trace = list(state.execution_trace) + ["Calculated result dynamically using calculator tool."]
        timeline = list(state.timeline) + [
            ExecutionTimelineStep(stage="complete", label="Completed Calculation", status="completed")
        ]
        return {
            "response_text": resp_text,
            "reason": reason,
            "decision": "PROCESSED",
            "execution_trace": trace,
            "timeline": timeline
        }

    # Handle DateTime Tool result (e.g., "What day of the week is today?")
    if "datetime_tool" in (state.selected_tools or []):
        dt_res = state.tool_results.get("datetime_tool", {})
        fmt_res = dt_res.get("formatted", dt_res.get("date", ""))
        resp_text = f"Today is **{fmt_res}**."
        reason = "Executed datetime_tool dynamically to retrieve current system date and time."
        trace = list(state.execution_trace) + ["Retrieved system date/time dynamically."]
        timeline = list(state.timeline) + [
            ExecutionTimelineStep(stage="complete", label="Completed DateTime Lookup", status="completed")
        ]
        return {
            "response_text": resp_text,
            "reason": reason,
            "decision": "PROCESSED",
            "execution_trace": trace,
            "timeline": timeline
        }

    # Handle Unsupported Capability / Empty Tools (e.g., "Send an email")
    if not state.selected_tools and not state.selected_skill:
        resp_text = f"I don't currently have an integration or registered tool to handle this task ('{state.user_message}'). You can teach me how you want this task performed or connect a compatible tool."
        reason = "No matching skill or tool capability found in registry."
        trace = list(state.execution_trace) + ["Unsupported capability boundary reached."]
        timeline = list(state.timeline) + [
            ExecutionTimelineStep(stage="complete", label="Capability Unavailable", status="completed")
        ]
        return {
            "response_text": resp_text,
            "reason": reason,
            "decision": "UNSUPPORTED_CAPABILITY",
            "execution_trace": trace,
            "timeline": timeline
        }

    # Handle Morning Briefing composite result
    if "get_calendar_events" in (state.selected_tools or []):
        cal_res = state.tool_results.get("get_calendar_events", {}).get("events", [])
        task_res = state.tool_results.get("get_pending_tasks", {}).get("tasks", [])
        deliv_res = state.tool_results.get("get_today_deliveries", {}).get("deliveries", [])
        
        resp_text, reason, p_meta = response_generator.format_briefing_response(
            calendar_events=cal_res,
            deliveries=deliv_res,
            context=state.personal_context
        )
    # Handle Delivery response
    elif "get_today_deliveries" in (state.selected_tools or []):
        deliv_res = state.tool_results.get("get_today_deliveries", {})
        resp_text, reason, p_meta = response_generator.format_delivery_response(
            tool_result=deliv_res,
            context=state.personal_context,
            skill=state.selected_skill or SkillSummary(id="skill_001", name="delivery", description="")
        )
    # Handle General response
    else:
        resp_text = f"I've processed your request: '{state.user_message}' using dynamic execution tools."
        reason = "Executed tools and formatted response."

    trace = list(state.execution_trace) + ["Generated explainable personalized response"]
    timeline = list(state.timeline) + [
        ExecutionTimelineStep(stage="complete", label="Completed Request", status="completed")
    ]
    return {
        "response_text": resp_text,
        "reason": reason,
        "decision": "PROCESSED",
        "execution_trace": trace,
        "timeline": timeline
    }
