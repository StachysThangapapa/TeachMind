# TeachMind Skill Schema

This document defines the canonical JSON representation of a **TeachMind Skill**, aligned with the Skill Memory vector search (`POST /skills/search`) and Agent execution components.

---

## Canonical JSON Schema Example

```json
{
  "id": "skill_001",
  "name": "refund_processing",
  "description": "Determine whether a customer qualifies for a product refund.",
  "version": "1.0",
  "confidence": 0.90,
  "triggers": [
    "customer refund request",
    "product return policy evaluation"
  ],
  "steps": [
    {
      "step": 1,
      "instruction": "Check purchase date relative to the 7-day return policy window."
    },
    {
      "step": 2,
      "instruction": "Verify whether the item was sold as final-sale or clearance."
    }
  ],
  "rules": [
    {
      "condition": "Purchase date is within 7 days of order",
      "action": "approve"
    },
    {
      "condition": "Product purchased past 7 days or marked clearance",
      "action": "reject"
    }
  ],
  "examples": [
    {
      "input": "Product purchased 3 days ago.",
      "expected": "approve"
    },
    {
      "input": "Normal product purchased 15 days ago.",
      "expected": "reject"
    }
  ],
  "exceptions": [
    {
      "condition": "Item arrived damaged upon delivery",
      "action": "approve"
    }
  ]
}
```

---

## Field Specifications

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `string` | Unique identifier for the skill (e.g., `skill_001`). |
| `name` | `string` | Short slug or title representing the skill. |
| `description` | `string` | Human-readable explanation of what the skill performs. |
| `version` | `string` | Skill version tracking (e.g., `1.0`, `1.1`). Increments upon human correction. |
| `confidence` | `float` | Verification accuracy score between `0.0` and `1.0`. |
| `triggers` | `array[string]` | Semantic intent triggers used by Skill Memory to index vector embeddings. |
| `steps` | `array[object]` | Sequential procedure steps (`step` number and `instruction`). |
| `rules` | `array[object]` | Structured conditional rules (`condition` logic and `action` output). |
| `examples` | `array[object]` | Sample input-to-expected-output demonstration pairs. |
| `exceptions` | `array[object]` | Human corrections and overriding rules added to resolve edge cases. |

---

## Skill Vector Search Response Wrapper (`POST /skills/search`)

When Skill Memory performs vector similarity search over skills, each hit is wrapped with similarity scoring:

```json
{
  "query": "Customer bought headphones 3 days ago. Can they get a refund?",
  "results": [
    {
      "skill_id": "skill_001",
      "name": "refund_processing",
      "similarity": 0.91,
      "skill": {
        "description": "Determine whether a customer qualifies for a product refund.",
        "triggers": [
          "customer refund request",
          "product return policy evaluation"
        ],
        "steps": [
          {
            "step": 1,
            "instruction": "Check purchase date relative to the 7-day return policy window."
          }
        ],
        "rules": [
          {
            "condition": "Purchase date is within 7 days of order",
            "action": "approve"
          }
        ],
        "examples": []
      }
    }
  ]
}
```
