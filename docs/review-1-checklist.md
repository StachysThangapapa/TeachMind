# TeachMind — Review 1 Readiness Checklist & Criteria Mapping

This document maps TeachMind's current repository state, architectural foundation, and integration deliverables against the official **Review 1 Hackathon Judging Criteria**.

---

## Criterion 1: UI/UX (Weight: 20%)

### Evidence to Show
- Clean, intuitive interface mockup/prototype showing the core Teach → Correct → Reuse loop.
- Interactive demonstration of teaching a new task via prompt/UI form.
- Visual display of learned skills, current skill versions (`v1.0`, `v1.1`), and accuracy confidence scores.

### Supporting Features & Specs
- `docs/api-contract.md`: Endpoints for `/skills/teach`, `/skills`, `/agent/execute`, `/skills/{id}/correct`.
- `frontend/` directory structure ready for Next.js / React component assembly.

### Pending / Next Steps for Teammate (Person 1: Frontend)
- [ ] Connect Next.js frontend pages to mock backend endpoints.
- [ ] Implement Skill Card component with version & confidence indicators.
- [ ] Build interactive correction modal to submit feedback.

---

## Criterion 2: Plan of Action (Weight: 20%)

### Evidence to Show
- Clear architectural blueprint and component boundaries.
- Defined contracts for Skill Schema, REST API endpoints, and Verification pipeline.
- GitHub Git branching strategy (`main` → `develop` → `feature/*`).

### Supporting Features & Specs
- `README.md`: System overview and development workflow.
- `docs/skill-schema.md`: Canonical JSON schema for skills.
- `docs/api-contract.md`: REST API specification.
- `.github/pull_request_template.md`: Standardized PR quality control.

### Pending / Next Steps
- [ ] Keep feature branches synced with `develop` using non-destructive workflow.

---

## Criterion 3: Impact & Use Case (Weight: 20%)

### Evidence to Show
- High-value business demonstration: Refund Eligibility Automation with edge-case learning.
- Ability for non-technical users to teach complex operational rules without code updates or model fine-tuning.

### Supporting Features & Specs
- `docs/verification-scenario.md`: Complete Teach → Store → Test → Verify → Correct → Update → Reuse narrative.
- `tests/scenarios/refund_processing.json`: Concrete test scenario covering standard rules, boundary limits, and damaged-product exceptions.

### Pending / Next Steps
- [ ] Prepare live or recorded presentation script following the 6-step verification scenario.

---

## Criterion 4: Feasibility (Weight: 15%)

### Evidence to Show
- Realistic technology stack choices (FastAPI, Next.js, LangGraph, PostgreSQL + pgvector).
- Modular design preventing vendor lock-in and allowing independent verification of mock or real agents.

### Supporting Features & Specs
- `backend/verification/evaluator.py`: Dependency-injected evaluator supporting mock callables today and LangGraph agent runners tomorrow.
- `.env.example`: Safe configuration template for environment variables.

### Pending / Next Steps for Teammate (Person 2: AI Agent)
- [ ] Connect LangGraph agent execution graph to `SkillEvaluator` interface.

---

## Criterion 5: Progress & Working MVP (Weight: 15%)

### Evidence to Show
- Verified working verification framework passing automated pytest tests.
- Functional test case loader, accuracy calculation module, and report generator.

### Supporting Features & Specs
- `backend/verification/metrics.py`: `calculate_accuracy` module.
- `backend/verification/evaluator.py`: `SkillEvaluator` class.
- `tests/test_verification.py`: 6 automated unit tests passing 100%.

### Pending / Next Steps for Teammates (Person 2: AI Agent & Person 3: Skill Memory)
- [ ] Implement FastAPI endpoint handlers referencing the API contract.
- [ ] Connect pgvector storage for vector search over stored skills.

---

## Criterion 6: Teamwork & Collaboration (Weight: 10%)

### Evidence to Show
- Active Git workflow with parallel feature branches (`feature/frontend`, `feature/ai-agent`, `feature/skill-memory`, `feature/verification`).
- Standardized PR templates ensuring code safety and secret prevention.

### Supporting Features & Specs
- `.gitignore`: Prevents accidental key/credential leakage.
- `.github/pull_request_template.md`: Enforces PR review standards.

### Pending / Next Steps
- [ ] Perform integration PR merges into `develop` as feature branches complete.
