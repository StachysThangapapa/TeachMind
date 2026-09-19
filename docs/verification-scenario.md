# TeachMind Core Validation Scenario: Teach → Store → Test → Verify → Correct → Update → Reuse

This document details the step-by-step validation contract for the primary TeachMind demonstration loop.

---

## Scenario Overview: Refund Policy Adaptation

The target scenario demonstrates how TeachMind captures human intent, stores it as a skill, encounters an edge case, receives a human correction, updates the skill version, and correctly reuses the updated rule on future inputs.

```
+-----------------------------------------------------------------------------------+
|  TEACH (v1.0)  -->  STORE  -->  TEST & VERIFY  -->  CORRECT (v1.1)  -->  REUSE    |
+-----------------------------------------------------------------------------------+
```

---

## Step-by-Step Workflow

### STEP 1: User Teaches Initial Skill
- **Action**: User provides natural language instruction to TeachMind.
- **Input Text**: `"Refund requests submitted within 7 days of purchase are approved."`
- **System Action**: AI Agent extracts rules and creates Skill object `refund_processing`.

### STEP 2: TeachMind Stores Skill Memory
- **State**: `skill_001` stored with version `1.0`.
- **Skill Object**:
```json
{
  "id": "skill_001",
  "name": "refund_processing",
  "description": "Determine customer refund eligibility.",
  "rules": ["Refund requests submitted within 7 days of purchase are approved."],
  "examples": [],
  "exceptions": [],
  "version": "1.0",
  "confidence": 0.90
}
```

### STEP 3: Agent Executes Task
- **Input**: `"Customer bought the product 3 days ago."`
- **Agent Result**: `APPROVE`
- **Verification Status**: **PASSED** (Purchased within 7-day window).

---

### STEP 4: Human Correction Introduced
- **Edge Case Encountered**: Agent rejects a damaged product bought 10 days ago.
- **User Correction**: `"Damaged products should be approved even when normally excluded or past the standard 7-day period."`

---

### STEP 5: Skill Memory Updated & Version Increment
- **State**: Skill version increments from `1.0` to `1.1`.
- **Updated Skill Object**:
```json
{
  "id": "skill_001",
  "name": "refund_processing",
  "description": "Determine customer refund eligibility.",
  "rules": ["Refund requests submitted within 7 days of purchase are approved."],
  "examples": [],
  "exceptions": [
    "Damaged products should be approved even when normally excluded or past the standard 7-day period."
  ],
  "version": "1.1",
  "confidence": 0.95
}
```

---

### STEP 6: Re-test & Re-use Verification
- **Input**: `"Clearance product bought 10 days ago and arrived damaged."`
- **Expected Decision**: `APPROVE`
- **Agent Result**: `APPROVE` (Matches exception rule added in v1.1).
- **Verification Status**: **PASSED**.

---

## Validation Contract Guarantee

This scenario represents the core benchmark for judging TeachMind's capability to learn without retraining underlying LLM parameters. All components must support this lifecycle contract for Review 1.
