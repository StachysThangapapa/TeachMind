# TeachMind

> A teachable AI assistant that learns user-specific tasks from instructions, demonstrations, and corrections without retraining the underlying model.

---

## Core Conceptual Loop

$$\text{TEACH} \longrightarrow \text{STORE} \longrightarrow \text{TEST} \longrightarrow \text{VERIFY} \longrightarrow \text{CORRECT} \longrightarrow \text{UPDATE} \longrightarrow \text{REUSE}$$

---

## Repository Structure

```text
TeachMind/
├── docs/                      # Architectural specs, skill schemas, and API contracts
│   ├── skill-schema.md
│   ├── api-contract.md
│   └── verification-scenario.md
├── backend/                   # FastAPI backend & verification framework
│   └── verification/          # Metrics, test loader, and skill evaluator
├── tests/                     # Automated test suites & verification scenarios
│   ├── scenarios/
│   └── test_verification.py
├── frontend/                  # Next.js / React frontend (in development)
├── .github/                   # PR templates & workflow configs
└── .env.example               # Environment configuration template
```

---

## Development Workflow

- `main` → Stable / Demo-ready
- `develop` → Integration branch
- `feature/*` → Feature-specific development (`feature/frontend`, `feature/ai-agent`, `feature/skill-memory`, `feature/verification`)

### Team Workflow Rules
1. Sync `develop`: `git checkout develop && git pull origin develop`
2. Create or checkout feature branch: `git checkout -b feature/your-feature`
3. Implement feature changes cleanly.
4. Run automated tests: `python -m pytest tests/`
5. Commit with descriptive messages.
6. Push feature branch: `git push -u origin feature/your-feature`
7. Open Pull Request into `develop` using the PR template.
8. Review, test, and merge into `develop`.
9. Delete feature branch when safely merged.

---

## Running Verification Tests

To execute the automated verification test suite locally:

```bash
python -m pytest tests/
```
