"""
FastAPI Router for TeachMind AI Agent Endpoints.
Exposes /agent/chat, /agent/execute, /agent/confirm, /agent/teach, and /agent/correct.
"""

from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.agent import (
    TaskExecutionRequest,
    TaskExecutionResponse,
    ConfirmActionRequest,
    ConfirmActionResponse,
)
from backend.app.agent.state import AgentState
from backend.app.agent.graph import agent_graph
from backend.app.tools.registry import tool_registry

router = APIRouter(prefix="/agent", tags=["AI Agent"])


@router.post("/chat", response_model=TaskExecutionResponse)
@router.post("/execute", response_model=TaskExecutionResponse)
async def execute_agent_task(request: TaskExecutionRequest) -> TaskExecutionResponse:
    """
    Executes a user request through the personalized agent state graph.
    """
    try:
        initial_state = AgentState(
            user_message=request.query,
            user_id=request.user_id,
            conversation_id=request.conversation_id or "conv_default"
        )
        final_state = agent_graph.run(initial_state)

        return TaskExecutionResponse(
            status="success",
            message=final_state.response_text,
            decision=final_state.decision,
            reason=final_state.reason,
            intent=final_state.intent,
            skill_used=final_state.selected_skill,
            similarity=final_state.similarity_score,
            confidence=final_state.selected_skill.confidence if final_state.selected_skill else 0.90,
            personalization={
                "match_score": final_state.personalization_match_score,
                "preferences_applied": final_state.personal_context.preferences.model_dump()
            },
            verification=final_state.verification_result,
            tool_executed=final_state.selected_tool,
            requires_confirmation=final_state.requires_confirmation,
            action_id=final_state.action_id,
            data={"response": final_state.response_text},
            execution_trace=final_state.execution_trace,
            timeline=final_state.timeline
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution error: {str(e)}"
        )


@router.post("/confirm", response_model=ConfirmActionResponse)
async def confirm_agent_action(request: ConfirmActionRequest) -> ConfirmActionResponse:
    """
    Handles confirmation response for mutating/high-impact actions.
    """
    if not request.confirmed:
        return ConfirmActionResponse(
            status="cancelled",
            message=f"Action '{request.action_id}' was cancelled by user.",
            action_id=request.action_id
        )

    # Execute confirming action (e.g. create_calendar_event)
    exec_res = tool_registry.execute_tool(
        name="create_calendar_event",
        arguments={"title": "ML Project Meeting", "time": "16:00", "date": "tomorrow"},
        user_confirmed=True
    )

    return ConfirmActionResponse(
        status="success",
        message=f"Action '{request.action_id}' confirmed and executed successfully.",
        action_id=request.action_id,
        data=exec_res.get("result")
    )
