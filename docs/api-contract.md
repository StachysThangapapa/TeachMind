# TeachMind API Contract

This document defines the REST API endpoints required for integration between the **Frontend**, **FastAPI Backend**, **AI Agent Orchestrator**, **Skill Memory (pgvector)**, and **Verification Framework**.

---

## Base URL
`/api/v1`

---

## Summary of Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/skills/teach` | Teach a new skill to TeachMind via instruction or demonstration. |
| `GET` | `/skills` | Retrieve all learned skills stored in Skill Memory. |
| `POST` | `/skills/search` | Search for relevant skills using vector similarity. |
| `POST` | `/agent/execute` | Execute a user task using active learned skills. |
| `POST` | `/skills/{skill_id}/correct` | Submit a human correction to refine an existing skill. |
| `POST` | `/skills/{skill_id}/validate` | Run automated verification scenarios against a skill. |

---

### 1. `POST /skills/search` (Skill Memory Vector Search)

**Purpose**: Performs vector similarity search over stored skill embeddings in `pgvector` to find matching skills for an incoming user task.

#### Request JSON
```json
{
  "query": "user's current task",
  "top_k": 3
}
```

#### Response JSON (`200 OK`)
```json
{
  "query": "user's current task",
  "results": [
    {
      "skill_id": "skill_001",
      "name": "refund_processing",
      "similarity": 0.91,
      "skill": {
        "description": "Determine whether a customer qualifies for a refund.",
        "triggers": [
          "customer refund request",
          "return policy"
        ],
        "steps": [
          {
            "step": 1,
            "instruction": "Check purchase date against standard 7-day refund window."
          }
        ],
        "rules": [
          {
            "condition": "Purchase within 7 days",
            "action": "approve"
          }
        ],
        "examples": []
      }
    }
  ]
}
```

---

### 2. `POST /skills/teach`

**Purpose**: Allows users to teach a new task through natural language instructions, rules, or demonstration text.

#### Request JSON
```json
{
  "name": "refund_processing",
  "description": "Determine whether a customer qualifies for a refund.",
  "triggers": ["refund request", "return policy"],
  "instruction": "Refund requests submitted within 7 days are approved.",
  "steps": [
    {
      "step": 1,
      "instruction": "Check purchase date against 7-day policy."
    }
  ],
  "rules": [
    {
      "condition": "Purchased within 7 days",
      "action": "approve"
    }
  ]
}
```

#### Response JSON (`201 Created`)
```json
{
  "status": "success",
  "message": "Skill successfully learned and stored.",
  "skill_id": "skill_001",
  "skill": {
    "id": "skill_001",
    "name": "refund_processing",
    "description": "Determine whether a customer qualifies for a refund.",
    "version": "1.0",
    "confidence": 0.90,
    "triggers": ["refund request"],
    "steps": [
      {
        "step": 1,
        "instruction": "Check purchase date against 7-day policy."
      }
    ],
    "rules": [
      {
        "condition": "Purchased within 7 days",
        "action": "approve"
      }
    ],
    "examples": [],
    "exceptions": []
  }
}
```

---

### 3. `GET /skills`

**Purpose**: List all skills stored in Skill Memory.

#### Request Query Parameters
- `limit` (optional, integer): Max items to return (default: `20`).

#### Response JSON (`200 OK`)
```json
{
  "total": 1,
  "skills": [
    {
      "id": "skill_001",
      "name": "refund_processing",
      "description": "Determine whether a customer qualifies for a refund.",
      "version": "1.0",
      "confidence": 0.90
    }
  ]
}
```

---

### 4. `POST /agent/execute`

**Purpose**: Execute an input task using matching learned skills retrieved via `/skills/search`.

#### Request JSON
```json
{
  "task": "Customer bought headphones 3 days ago. Can they get a refund?",
  "skill_id": "skill_001"
}
```

#### Response JSON (`200 OK`)
```json
{
  "skill_id": "skill_001",
  "decision": "approve",
  "reason": "Purchase is within the seven-day refund period.",
  "confidence": 0.94,
  "matched_similarity": 0.91,
  "execution_time_ms": 142
}
```

---

### 5. `POST /skills/{skill_id}/correct`

**Purpose**: Submit human feedback/correction for a specific skill when an agent decision is wrong or incomplete.

#### Request JSON
```json
{
  "correction": "Damaged products should be approved even when normally excluded or past 7 days.",
  "task_context": "Clearance product bought 10 days ago and arrived damaged."
}
```

#### Response JSON (`200 OK`)
```json
{
  "status": "success",
  "message": "Skill updated with new exception rule.",
  "skill": {
    "id": "skill_001",
    "name": "refund_processing",
    "version": "1.1",
    "confidence": 0.95,
    "exceptions": [
      {
        "condition": "Damaged product upon delivery",
        "action": "approve"
      }
    ]
  }
}
```

---

### 6. `POST /skills/{skill_id}/validate`

**Purpose**: Run automated verification scenarios against a skill to calculate accuracy and validate performance.

#### Request JSON
```json
{
  "test_scenario_id": "refund_processing"
}
```

#### Response JSON (`200 OK`)
```json
{
  "skill_id": "skill_001",
  "total_cases": 5,
  "correct": 5,
  "incorrect": 0,
  "accuracy": 1.00,
  "results": [
    {
      "input": "Product purchased 3 days ago.",
      "expected": "approve",
      "actual": "approve",
      "passed": true
    }
  ]
}
```
