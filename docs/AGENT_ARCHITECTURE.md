# TeachMind AI Agent Architecture

This document specifies the technical architecture, LangGraph state graph, intent engine, personal context representation, tool registry, and integration contracts for the **TeachMind Personalized AI Agent**.

---

## 1. System Vision & Core Differentiator

TeachMind is a **Personalized AI Agent That Learns How You Work**. Unlike generic AI assistants that apply a single static prompt to every user, TeachMind maintains a persistent **Personalized Behavioral Layer** around an agent.

```
                           USER
                            |
                            v
                      USER REQUEST
                            |
                            v
                +-----------------------+
                | PERSONAL CONTEXT      |
                | - Preferences         |
                | - Habits              |
                | - Constraints         |
                | - Corrections         |
                | - Permissions         |
                +-----------+-----------+
                            |
                            v
                   INTENT UNDERSTANDING
                            |
                            v
                    SKILL RETRIEVAL
                            |
                            v
                    PERSONALIZED SKILL
                            |
                            v
                       PLANNER
                            |
                            v
                       VERIFICATION
                            |
                  +---------+---------+
                  |                   |
                PASS                FAIL
                  |                   |
                  v                   v
             TOOL GATEWAY       CORRECTION FLOW
                  |
                  v
            TOOL EXECUTION
                  |
                  v
               RESULT
                  |
                  v
         PERSONALIZED RESPONSE
                  |
                  v
          USER FEEDBACK/CORRECTION
                  |
                  v
         UPDATE PERSONAL SKILL
                  |
                  v
            RE-VERIFICATION
```

---

## 2. Existing Modules & Integration Discovery

Through inspection of the repository:

1. **Skill Memory & Schema (`docs/skill-schema.md`, `docs/api-contract.md`)**:
   - Endpoint: `POST /skills/search` (accepts `query`, `top_k`, returns similarity-ranked skills).
   - Canonical Skill Object: `id`, `name`, `version`, `confidence`, `triggers`, `steps`, `rules`, `examples`, `exceptions`.
2. **Verification System (`backend/verification/`)**:
   - `backend/verification/evaluator.py` (`SkillEvaluator`)
   - `backend/verification/metrics.py` (`calculate_accuracy`)
   - `backend/verification/test_cases.py` (`TestCaseLoader`)
3. **Frontend API Contracts (`frontend/src/lib/api/agent.ts`, `frontend/src/lib/types/agent.ts`)**:
   - Endpoints: `POST /agent/execute`, `POST /agent/chat`, `POST /agent/confirm`.
   - Data Types: `TaskExecutionResult`, `ExecutionTimelineStep`, `CanonicalSkill`.

---

## 3. LangGraph Agent Lifecycle Graph

The agent workflow is modeled as a state machine using **LangGraph**:

```
START
  │
  ▼
load_context
  │
  ▼
understand_intent ──► (TEACH_REQUEST / CORRECTION) ──► process_teaching_or_correction ──► END
  │
  ▼
retrieve_skills
  │
  ▼
select_personalized_skill
  │
  ▼
plan
  │
  ▼
verify
  │
  ├──► [VERIFICATION_FAILED] ──► correction_flow ──► END
  ├──► [CONFIRMATION_REQUIRED] ──► request_confirmation ──► END
  │
  ▼ [VERIFIED]
tool_selection
  │
  ▼
tool_execution
  │
  ▼
personalized_response
  │
  ▼
END
```

---

## 4. Module Decomposition

### `backend/app/agent/`
- `state.py`: Strongly typed `AgentState` Pydantic model.
- `graph.py`: LangGraph state graph construction and compilation.
- `nodes.py`: Node execution logic (`load_context`, `understand_intent`, `retrieve_skills`, `select_personalized_skill`, `plan`, `verify`, `execute_tool`, `generate_response`).
- `intent.py`: Structured intent classification engine (`NORMAL_REQUEST`, `TEACH_REQUEST`, `CORRECTION`, `CLARIFICATION`, `CONFIRMATION`, `CANCELLATION`).
- `context.py`: Personal context & preference manager.
- `personalization.py`: Personalization match scorer & preference conflict detector.
- `correction.py`: Correction learning & version increment handler (`v1.0` -> `v1.1`).
- `planner.py`: Composable workflow planner.
- `prompts.py`: Modular LLM prompt templates.

### `backend/app/tools/`
- `base.py`: Abstract `BaseTool` interface with permission levels (`READ_ONLY`, `MUTATING`, `HIGH_IMPACT`).
- `registry.py`: Central secure tool registry with allow-listing.
- `delivery.py`: `GetTodayDeliveriesTool` (Mock implementation for delivery scenario).
- `calendar.py`: `GetCalendarEventsTool` & `CreateCalendarEventTool` (Mock implementation for morning briefing & scheduling).

### `backend/app/api/`
- `agent.py`: FastAPI router providing `/agent/chat`, `/agent/execute`, `/agent/confirm`, `/agent/teach`, `/agent/correct`.

---

## 5. Security & Autonomy Boundaries

- **Tool Execution**: Tools are strictly restricted to registered python callables. Arbitrary code, HTTP requests, or shell commands are forbidden.
- **Permission Boundary**:
  - `READ_ONLY`: Executed automatically.
  - `MUTATING`: Requires explicit user confirmation via `/agent/confirm`.
  - `HIGH_IMPACT`: Requires multi-factor / explicit step confirmation.
