"""
Adapter between Canonical Skill Memory schemas (backend/schemas/skill.py)
and AI Agent schemas (backend/app/schemas/agent.py).
"""

from typing import Dict, Any, List, Union
from backend.schemas.skill import (
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    StepSchema,
    RuleSchema,
    ExampleSchema,
)
from backend.app.schemas.agent import SkillSummary as AgentSkillSummary


def canonical_to_agent_summary(skill: Union[SkillResponse, Dict[str, Any]]) -> AgentSkillSummary:
    """Converts a canonical SkillResponse ORM/Pydantic model to AgentSkillSummary."""
    if isinstance(skill, dict):
        s_id = skill.get("skill_id") or skill.get("id") or "skill_default"
        s_name = skill.get("name") or "generic_skill"
        s_desc = skill.get("description") or ""
        v_raw = skill.get("version", 1)
        if isinstance(v_raw, int):
            s_ver = f"1.{v_raw - 1}" if v_raw > 1 else "1.0"
        else:
            s_ver = str(v_raw) if "." in str(v_raw) else f"{v_raw}.0"
        s_trig = skill.get("triggers") or []
        s_steps = skill.get("steps") or []
        s_rules = skill.get("rules") or []
        s_ex = skill.get("examples") or []
        s_exc = skill.get("exceptions") or []
    else:
        s_id = skill.skill_id
        s_name = skill.name
        s_desc = skill.description
        v_raw = skill.version
        if isinstance(v_raw, int):
            s_ver = f"1.{v_raw - 1}" if v_raw > 1 else "1.0"
        else:
            s_ver = str(v_raw) if "." in str(v_raw) else f"{v_raw}.0"
        s_trig = skill.triggers
        s_steps = [s.model_dump() if hasattr(s, "model_dump") else s for s in skill.steps]
        s_rules = [r.model_dump() if hasattr(r, "model_dump") else r for r in skill.rules]
        s_ex = [e.model_dump() if hasattr(e, "model_dump") else e for e in skill.examples]
        s_exc = []



    return AgentSkillSummary(
        id=s_id,
        name=s_name,
        description=s_desc,
        version=s_ver,
        confidence=0.95,
        triggers=s_trig,
        steps=s_steps,
        rules=s_rules,
        exceptions=s_exc
    )


def agent_summary_to_canonical_create(agent_skill: AgentSkillSummary, user_id: str = "user_default") -> SkillCreate:
    """Converts an AgentSkillSummary to a canonical SkillCreate schema."""
    steps = []
    for i, s in enumerate(agent_skill.steps):
        if isinstance(s, dict):
            step_num = s.get("step", i + 1)
            instr = s.get("instruction") or s.get("action") or f"Step {i+1}"
        else:
            step_num = getattr(s, "step", i + 1)
            instr = getattr(s, "instruction", f"Step {i+1}")
        steps.append(StepSchema(step=int(step_num), instruction=str(instr)))

    rules = []
    for r in agent_skill.rules:
        if isinstance(r, dict):
            cond = r.get("condition", "general")
            act = r.get("action", "execute")
        else:
            cond = getattr(r, "condition", "general")
            act = getattr(r, "action", "execute")
        rules.append(RuleSchema(condition=str(cond), action=str(act)))

    # Include exceptions as conditional rules
    for exc in agent_skill.exceptions:
        if isinstance(exc, dict):
            cond = exc.get("condition", "exception")
            act = exc.get("action", "override")
        else:
            cond = getattr(exc, "condition", "exception")
            act = getattr(exc, "action", "override")
        rules.append(RuleSchema(condition=str(cond), action=str(act)))

    # Compute integer version
    try:
        ver_int = int(float(agent_skill.version))
    except Exception:
        ver_int = 1

    skill_id = agent_skill.id
    if not skill_id or skill_id == "skill_001":
        skill_id = f"skill_{user_id}_{agent_skill.name.lower().replace(' ', '_')}"
    elif user_id != "user_default" and user_id not in skill_id:
        skill_id = f"skill_{user_id}_{agent_skill.name.lower().replace(' ', '_')}"

    return SkillCreate(
        skill_id=skill_id,
        name=agent_skill.name,
        description=agent_skill.description or f"Procedural workflow for {agent_skill.name}",
        triggers=agent_skill.triggers or [agent_skill.name.lower()],
        steps=steps,
        rules=rules,
        examples=[],
        version=ver_int,
        verified=True
    )



def agent_summary_to_canonical_update(agent_skill: AgentSkillSummary) -> SkillUpdate:
    """Converts an updated AgentSkillSummary to a canonical SkillUpdate schema."""
    steps = []
    for i, s in enumerate(agent_skill.steps):
        if isinstance(s, dict):
            step_num = s.get("step", i + 1)
            instr = s.get("instruction") or s.get("action") or f"Step {i+1}"
        else:
            step_num = getattr(s, "step", i + 1)
            instr = getattr(s, "instruction", f"Step {i+1}")
        steps.append(StepSchema(step=int(step_num), instruction=str(instr)))

    rules = []
    for r in agent_skill.rules + agent_skill.exceptions:
        if isinstance(r, dict):
            cond = r.get("condition", "general")
            act = r.get("action", "execute")
        else:
            cond = getattr(r, "condition", "general")
            act = getattr(r, "action", "execute")
        rules.append(RuleSchema(condition=str(cond), action=str(act)))

    return SkillUpdate(
        name=agent_skill.name,
        description=agent_skill.description,
        triggers=agent_skill.triggers,
        steps=steps,
        rules=rules,
        verified=True
    )
