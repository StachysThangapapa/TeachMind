# TeachMind Skill Schema

This document defines the canonical JSON representation of a **TeachMind Skill**. All components (Frontend, AI Agent, Skill Memory, and Verification) must adhere to this schema when creating, storing, reading, or updating skills.

---

## Canonical JSON Schema Example

```json
{
  "id": "skill_001",
  "name": "refund_processing",
  "description": "Determine whether a customer qualifies for a product refund.",
  "rules": [
    "Refund requests submitted within 7 days of purchase are approved by default.",
    "Clearance or final-sale items are non-refundable unless damaged."
  ],
  "examples": [
    "Input: 'Purchased 3 days ago' -> Result: APPROVE",
    "Input: 'Purchased 15 days ago' -> Result: REJECT"
  ],
  "exceptions": [
    "Damaged products should be approved even if purchased past the standard 7-day period or marked as clearance."
  ],
  "version": "1.1",
  "confidence": 0.92
}
```

---

## Field Specifications

| Field | Type | Origin | System vs User Generated | Description |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `string` | System | System | Unique identifier for the skill (e.g., `skill_001`, UUID, or slug). |
| `name` | `string` | User / System | User/System | Short, human-readable identifier for the skill (snake_case or clean string). |
| `description` | `string` | User | User | Overview of what the skill does and when it should be applied. |
| `rules` | `array[string]` | User / Agent | User Teaching | Standard business logic, guidelines, or conditions learned from instructions. |
| `examples` | `array[string]` | User / Agent | User Teaching | Explicit input-output pairs or demonstrations showing expected behavior. |
| `exceptions` | `array[string]` | User Correction | User Correction | Special edge cases or overriding rules added when users correct erroneous agent decisions. |
| `version` | `string` | System | System | Version tracking string (e.g., `1.0`, `1.1`). Increments upon human correction. |
| `confidence` | `float` | System | System | Self-assessed or empirical score (0.0 to 1.0) indicating skill reliability based on test accuracy. |

---

## Lifecycle & Versioning Rules

1. **Initial Teaching (`v1.0`)**: When a user teaches a skill via natural language or demonstration, the AI Agent extracts `rules` and initial `examples`, assigning initial version `1.0` and default confidence score (e.g., `0.90`).
2. **Correction & Update (`v1.x`)**:
   - When an agent decision is corrected by a human user, the correction is appended to `exceptions` or refines `rules`.
   - The minor version increments (e.g., `1.0` → `1.1` → `1.2`).
   - If a structural rewrite occurs, the major version increments (e.g., `1.1` → `2.0`).
3. **Verification & Confidence**:
   - Running verification test suites against a skill updates the `confidence` score based on evaluation accuracy.
