# TeachMind API Contract

This document defines the REST API endpoints required for integration between the **Frontend**, **Backend**, **AI Agent Orchestrator**, **Skill Memory**, and **Verification Framework**.

---

## Base URL
`/api/v1`

---

## Summary of Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/skills/teach` | Teach a new skill to TeachMind via instruction or demonstration. |
| `GET` | `/skills` | Retrieve all learned skills or filter by query/ID. |
| `POST` | `/agent/execute` | Execute a user task using active/relevant learned skills. |
| `POST` | `/skills/{skill_id}/correct` | Submit a human correction to refine an existing skill. |
| `POST` | `/skills/{skill_id}/validate` | Run verification test cases against a skill to calculate accuracy. |

---

### 1. `POST /skills/teach`

**Purpose**: Allows users to teach a new task through natural language instructions, rules, or demonstration text.

#### Request JSON
```json
{
  "name": "refund_processing",
  "description": "Determine whether a customer qualifies for a refund.",
  "instruction": "Refund requests submitted within 7 days are approved.",
  "examples": [
    "Purchased 3 days ago -> approve"
  ]
}
```

#### Response JSON (`201 Created`)
```json
{
  "status": "success",
  "message": "Skill successfully learned and stored.",
  "skill": {
    "id": "skill_001",
    "name": "refund_processing",
    "description": "Determine whether a customer qualifies for a refund.",
    "rules": [
      "Refund requests submitted within 7 days are approved."
    ],
    "examples": [
      "Purchased 3 days ago -> approve"
    ],
    "exceptions": [],
    "version": "1.0",
    "confidence": 0.90
  }
}
```

#### Error Responses
- `400 Bad Request`: Missing mandatory fields (`name`, `instruction`).
```json
{
  "error": "BAD_REQUEST",
  "message": "Field 'instruction' is required."
}
```

---

### 2. `GET /skills`

**Purpose**: List all skills stored in Skill Memory.

#### Request Query Parameters
- `query` (optional, string): Filter skills by search query.
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
      "rules": [
        "Refund requests submitted within 7 days are approved."
      ],
      "examples": [
        "Purchased 3 days ago -> approve"
      ],
      "exceptions": [],
      "version": "1.0",
      "confidence": 0.90
    }
  ]
}
```

---

### 3. `POST /agent/execute`

**Purpose**: Execute an input task using matching learned skills.

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
  "execution_time_ms": 142
}
```

#### Error Responses
- `404 Not Found`: Specified `skill_id` does not exist.
```json
{
  "error": "SKILL_NOT_FOUND",
  "message": "Skill with id 'skill_999' was not found."
}
```

---

### 4. `POST /skills/{skill_id}/correct`

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
    "description": "Determine whether a customer qualifies for a refund.",
    "rules": [
      "Refund requests submitted within 7 days are approved."
    ],
    "examples": [
      "Purchased 3 days ago -> approve"
    ],
    "exceptions": [
      "Damaged products should be approved even when normally excluded or past 7 days."
    ],
    "version": "1.1",
    "confidence": 0.95
  }
}
```

#### Error Responses
- `404 Not Found`: Skill ID does not exist.

---

### 5. `POST /skills/{skill_id}/validate`

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
  "total_cases": 4,
  "correct": 4,
  "incorrect": 0,
  "accuracy": 1.00,
  "results": [
    {
      "input": "Product purchased 3 days ago.",
      "expected": "approve",
      "actual": "approve",
      "passed": true
    },
    {
      "input": "Normal product purchased 15 days ago.",
      "expected": "reject",
      "actual": "reject",
      "passed": true
    },
    {
      "input": "Clearance product purchased 2 days ago.",
      "expected": "reject",
      "actual": "reject",
      "passed": true
    },
    {
      "input": "Clearance product purchased 2 days ago and arrived damaged.",
      "expected": "approve",
      "actual": "approve",
      "passed": true
    }
  ]
}
```
