# TeachMind — Skill Memory Backend Requirements for Review 1

## 1. Project Goal

TeachMind is a teachable AI assistant that learns how the user works.

The user teaches TeachMind a task through instructions or demonstrations. TeachMind converts what it learned into a reusable Skill, stores it in Skill Memory, and later retrieves that Skill when the user gives a related task.

Core loop:

```text
Teach → Test → Verify → Correct → Reuse
```

For Review 1, the Skill Memory implementation should support the following end-to-end flow:

```text
User teaches a workflow
        ↓
LLM extracts Skill JSON
        ↓
User reviews/verifies the learned skill
        ↓
Skill is stored
        ↓
Embedding is generated
        ↓
Embedding is stored in pgvector
        ↓
User gives a new related task
        ↓
AI Agent searches Skill Memory
        ↓
Relevant Skill JSON is retrieved
        ↓
AI Agent uses the learned workflow
```

The goal is a working MVP, not the complete final Skill Memory system.

---

# 2. Skill Memory Responsibility

Skill Memory answers:

> "What has this user taught TeachMind?"

It is responsible for:

- storing learned skills
- validating Skill JSON
- generating/storing embeddings
- retrieving relevant skills
- returning Skill JSON to the AI Agent
- keeping basic verification/version information

Skill Memory should **not**:

- execute desktop actions
- control applications
- perform the workflow itself
- make final execution decisions
- replace the AI Agent

The separation is:

```text
Skill Memory
"What did the user teach me?"

AI Agent
"Given the current task and the learned skill, what should I do?"

Desktop Tools
"Actually perform the action."
```

---

# 3. Review 1 Scope

## Required

### 3.1 PostgreSQL Database

Use PostgreSQL as the Skill Memory database.

Enable the `pgvector` extension for semantic search.

The main `skills` table should contain:

| Field | Purpose |
|---|---|
| `skill_id` | Unique skill identifier |
| `name` | Human-readable skill name |
| `description` | Description of the workflow |
| `triggers` | Phrases that can indicate when the skill should be used |
| `steps` | Ordered workflow instructions |
| `rules` | Conditional instructions |
| `examples` | Example inputs and expected behavior |
| `version` | Skill version |
| `verified` | Whether the user verified the skill |
| `embedding` | Vector representation for semantic retrieval |
| `created_at` | Creation timestamp |
| `updated_at` | Last update timestamp |

A practical PostgreSQL representation can use JSONB for structured fields:

```text
skills
├── skill_id
├── name
├── description
├── triggers       JSONB
├── steps          JSONB
├── rules          JSONB
├── examples       JSONB
├── version
├── verified
├── embedding      VECTOR
├── created_at
└── updated_at
```

---

# 4. Canonical Skill JSON

All learned skills should follow this structure:

```json
{
  "skill_id": "skill_001",
  "name": "skill_name",
  "description": "Description of the learned workflow.",
  "triggers": [
    "trigger phrase 1",
    "trigger phrase 2"
  ],
  "steps": [
    {
      "step": 1,
      "instruction": "First workflow instruction."
    },
    {
      "step": 2,
      "instruction": "Second workflow instruction."
    }
  ],
  "rules": [
    {
      "condition": "condition",
      "action": "action"
    }
  ],
  "examples": [
    {
      "input": "Example user request.",
      "expected_behavior": "Expected behavior."
    }
  ],
  "version": 1,
  "verified": true,
  "metadata": {
    "created_at": "2026-09-19T10:00:00Z",
    "updated_at": "2026-09-19T10:00:00Z"
  }
}
```

This schema is the contract between:

```text
LLM Skill Extraction
        ↓
Skill Memory
        ↓
AI Agent
```

Do not create a different Skill structure for the Review 1 implementation.

---

# 5. API 1 — Skill Extraction

## Endpoint

```http
POST /skills/extract
```

Purpose:

Convert the user's teaching input into a Skill JSON.

Example request:

```json
{
  "instruction": "I want to teach you how I prepare my monthly report. I take the sales CSV, create an Excel report, add a summary sheet and chart, then save it in my Reports folder."
}
```

Example response:

```json
{
  "skill": {
    "skill_id": "skill_001",
    "name": "Process Monthly Report",
    "description": "Create a monthly Excel report from a sales CSV.",
    "triggers": [
      "prepare monthly report",
      "create monthly sales report"
    ],
    "steps": [
      {
        "step": 1,
        "instruction": "Use the provided sales CSV as the input."
      },
      {
        "step": 2,
        "instruction": "Create an Excel report."
      },
      {
        "step": 3,
        "instruction": "Add a summary sheet."
      },
      {
        "step": 4,
        "instruction": "Add a chart."
      },
      {
        "step": 5,
        "instruction": "Save the report in the user's Reports folder."
      }
    ],
    "rules": [],
    "examples": [],
    "version": 1,
    "verified": false
  }
}
```

Important:

`/skills/extract` should extract the skill but should **not automatically mark it as verified**.

The user should be able to review the extracted Skill before it is treated as a verified learned skill.

---

# 6. Verification

The Review 1 flow should include user verification.

```text
Teaching Input
      ↓
Skill Extraction
      ↓
Show Skill JSON / Human-readable Skill
      ↓
User verifies
      ↓
Store verified skill
```

After verification:

```json
"verified": true
```

For Review 1, a simple verification mechanism is sufficient.

A complex correction-learning system is not required yet.

---

# 7. API 2 — Store Skill

## Endpoint

```http
POST /skills
```

Purpose:

Validate and store a verified Skill JSON.

Example request:

```json
{
  "skill_id": "skill_001",
  "name": "Process Monthly Report",
  "description": "Create a monthly Excel report from a sales CSV.",
  "triggers": [
    "prepare monthly report",
    "create monthly sales report"
  ],
  "steps": [
    {
      "step": 1,
      "instruction": "Use the provided sales CSV as the input."
    },
    {
      "step": 2,
      "instruction": "Create an Excel report."
    },
    {
      "step": 3,
      "instruction": "Add a summary sheet."
    },
    {
      "step": 4,
      "instruction": "Add a chart."
    },
    {
      "step": 5,
      "instruction": "Save the report in the user's Reports folder."
    }
  ],
  "rules": [],
  "examples": [],
  "version": 1,
  "verified": true
}
```

The backend should:

1. validate the Skill JSON
2. generate the skill's embedding
3. store the Skill JSON
4. store the embedding in pgvector
5. return the stored skill

---

# 8. Embedding Generation

Each verified skill should have an embedding for semantic retrieval.

The embedding input should be constructed from meaningful skill information, such as:

```text
Name
Description
Triggers
Steps
Rules
Examples
```

Example conceptual text:

```text
Process Monthly Report

Create a monthly Excel report from a sales CSV.

Triggers:
prepare monthly report
create monthly sales report

Steps:
Use the sales CSV as input.
Create an Excel report.
Add a summary sheet.
Add a chart.
Save the report in the Reports folder.
```

The resulting vector is stored in:

```text
skills.embedding
```

using PostgreSQL + pgvector.

The exact embedding model can be selected by the implementation team, as long as the same embedding space is used for stored skills and search queries.

---

# 9. API 3 — Skill Search

This API contract is fixed.

## Endpoint

```http
POST /skills/search
```

## Request

```json
{
  "query": "user's current task",
  "top_k": 3
}
```

## Response

```json
{
  "query": "user's current task",
  "results": [
    {
      "skill_id": "skill_001",
      "name": "skill_name",
      "similarity": 0.91,
      "skill": {
        "description": "...",
        "triggers": [
          "..."
        ],
        "steps": [
          {
            "step": 1,
            "instruction": "..."
          }
        ],
        "rules": [
          {
            "condition": "...",
            "action": "..."
          }
        ],
        "examples": []
      }
    }
  ]
}
```

Do not change this contract unless the integration requirements change later.

---

# 10. Skill Search Implementation

When the AI Agent calls:

```http
POST /skills/search
```

the backend should:

```text
User's current task
        ↓
Generate query embedding
        ↓
Search Skill embeddings using pgvector
        ↓
Calculate similarity
        ↓
Return top K skills
```

Example:

User says:

```text
"Can you make this month's sales report?"
```

The search query may retrieve:

```text
Process Monthly Report
```

even if the stored trigger was:

```text
"prepare monthly report"
```

This demonstrates that the system is doing semantic retrieval rather than exact keyword matching.

---

# 11. AI Agent Integration

The AI Agent should use Skill Memory when handling a task.

Example:

```text
User:
"Create this month's sales report."
```

The Agent:

```text
1. Understands the current task
        ↓
2. Calls POST /skills/search
        ↓
3. Receives relevant Skill JSON
        ↓
4. Interprets the learned workflow
        ↓
5. Plans execution
        ↓
6. Selects appropriate tools
        ↓
7. Executes the workflow
        ↓
8. Verifies the result
        ↓
9. Reports the result to the user
```

The important architecture is:

```text
USER
  ↓
AI AGENT
  ↓
POST /skills/search
  ↓
SKILL MEMORY
  ↓
Relevant Skill JSON
  ↓
AI AGENT
  ↓
Desktop Tools
  ↓
Result
```

Skill Memory only retrieves the learned workflow.

The AI Agent is responsible for deciding how to apply it.

---

# 12. Sample Skills for Review 1

Create at least 3–5 realistic skills so semantic retrieval can be demonstrated.

Recommended examples:

### Skill 1 — Process Monthly Report

```text
Input:
Sales CSV

Workflow:
Create Excel report
→ add summary
→ add chart
→ save to Reports folder
```

### Skill 2 — Format Excel Report

```text
Input:
Existing Excel report

Workflow:
Open report
→ format headers
→ adjust columns
→ apply required formatting
→ save
```

### Skill 3 — Customer Email Workflow

```text
Input:
Customer message

Workflow:
Read message
→ identify request type
→ draft response
→ apply user's email rules
→ prepare/send response
```

### Skill 4 — Organize Project Files

```text
Input:
Project files

Workflow:
Identify file types
→ organize into folders
→ apply naming rules
→ verify organization
```

### Skill 5 — Process Support Tickets

```text
Input:
Support tickets

Workflow:
Read ticket
→ classify issue
→ apply learned categorization rules
→ update ticket
→ verify result
```

Only 3–5 are needed for Review 1.

---

# 13. Minimum Review 1 APIs

The minimum required backend API set is:

```text
POST /skills/extract
POST /skills
POST /skills/search
```

Optional:

```text
GET /skills
```

`GET /skills` can be used by the frontend to display the user's learned skills.

Example:

```http
GET /skills
```

Possible response:

```json
{
  "skills": [
    {
      "skill_id": "skill_001",
      "name": "Process Monthly Report",
      "verified": true,
      "version": 1
    }
  ]
}
```

---

# 14. Database + API Architecture

The Review 1 backend should look like:

```text
                    ┌──────────────────┐
                    │   TeachMind UI   │
                    └────────┬─────────┘
                             │
                             ↓
                    ┌──────────────────┐
                    │    Backend API   │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ↓                             ↓
      /skills/extract                  /skills/search
              ↓                             ↓
       LLM Skill Extraction          Query Embedding
              ↓                             ↓
        Skill JSON                  pgvector Search
              │                             │
              └──────────────┬──────────────┘
                             ↓
                    ┌──────────────────┐
                    │ PostgreSQL       │
                    │ + pgvector       │
                    └────────┬─────────┘
                             │
                             ↓
                       Skill JSON
                             │
                             ↓
                        AI Agent
                             │
                             ↓
                       Desktop Tools
```

---

# 15. Review 1 End-to-End Demo

The demo should show actual learning and reuse.

## Step 1 — Teach

User:

```text
I want to teach you how I prepare my monthly sales report.

I take the sales CSV, create an Excel report, add a summary sheet,
add a chart, and save it in my Reports folder.
```

## Step 2 — Extract

TeachMind calls:

```http
POST /skills/extract
```

LLM generates Skill JSON.

## Step 3 — Verify

TeachMind shows:

```text
Learned Skill:
Process Monthly Report

1. Use the sales CSV
2. Create Excel report
3. Add summary sheet
4. Add chart
5. Save to Reports folder

[Verify]
```

User verifies it.

## Step 4 — Store

TeachMind calls:

```http
POST /skills
```

The backend:

```text
Validate
→ Generate embedding
→ Store in PostgreSQL
→ Store vector in pgvector
```

## Step 5 — New Task

Later the user says:

```text
Create this month's sales report.
```

This wording does not need to exactly match the original teaching input.

## Step 6 — Retrieve

AI Agent calls:

```http
POST /skills/search
```

with:

```json
{
  "query": "Create this month's sales report.",
  "top_k": 3
}
```

Skill Memory returns:

```text
Process Monthly Report
```

with a similarity score.

## Step 7 — Apply

The AI Agent interprets the Skill JSON and uses available tools to perform the workflow.

## Step 8 — Verify

The Agent checks whether the expected output was produced.

## Step 9 — Result

The user sees that the task was completed using the workflow they previously taught TeachMind.

This is the most important Review 1 demonstration.

---

# 16. What Does NOT Need to Be Fully Implemented for Review 1

Do not spend Review 1 time building the complete final Skill Memory system.

The following can be deferred:

```text
Complex correction learning
Multiple skill versions
Skill merging
Conflict resolution
Autonomous skill discovery
Advanced demonstration/action tracking
Perfect desktop automation
Advanced failure recovery
Complex analytics
Automatic skill optimization
```

These are future phases.

For Review 1, the priority is a working:

```text
Teach
  ↓
Extract
  ↓
Verify
  ↓
Store
  ↓
Embed
  ↓
Retrieve
  ↓
Agent
  ↓
Execute
  ↓
Result
```

---

# 17. Review 1 Completion Checklist

## Database

- [ ] PostgreSQL configured
- [ ] pgvector enabled
- [ ] `skills` table created
- [ ] JSONB fields configured
- [ ] embedding/vector field configured

## Skill Creation

- [ ] Skill JSON schema finalized
- [ ] `POST /skills/extract` implemented
- [ ] LLM extraction implemented
- [ ] Verification flow implemented
- [ ] `POST /skills` implemented
- [ ] Skill validation implemented

## Embeddings

- [ ] Embedding generation implemented
- [ ] Skill embedding stored
- [ ] pgvector index/search configured

## Retrieval

- [ ] `POST /skills/search` implemented
- [ ] Query embedding generated
- [ ] Semantic similarity search working
- [ ] Top-K results returned
- [ ] Required response contract preserved

## Agent Integration

- [ ] AI Agent can call `/skills/search`
- [ ] Agent receives Skill JSON
- [ ] Agent can interpret learned steps
- [ ] Agent can pass the workflow to desktop tools
- [ ] Basic result verification implemented

## Demo

- [ ] At least 3–5 sample skills
- [ ] User can teach a skill
- [ ] Skill can be extracted
- [ ] User can verify it
- [ ] Skill is stored
- [ ] Embedding is stored
- [ ] New differently-worded task retrieves the correct skill
- [ ] Agent uses the retrieved skill
- [ ] Result is shown to the user

---

# 18. Final Review 1 Milestone

The Skill Memory part is considered successful for Review 1 when this works:

```text
                    TEACH
                      ↓
              User teaches task
                      ↓
              LLM extracts Skill
                      ↓
                   VERIFY
                      ↓
              Skill Memory stores
                      ↓
             Generate embedding
                      ↓
                pgvector
                      ↓
            User gives new task
                      ↓
                 AI Agent
                      ↓
              /skills/search
                      ↓
             Relevant Skill JSON
                      ↓
                AI Agent
                      ↓
              Desktop Tools
                      ↓
                 VERIFY
                      ↓
                  RESULT
```

The key proof is:

> TeachMind can remember a workflow taught by the user and retrieve that workflow when the user later asks for a related task using different wording.

That is the core Skill Memory capability required for Review 1.

---

# 19. Future Skill Memory Phases

After Review 1, the system can be extended with:

```text
Phase 1   Skill Schema + Database
Phase 2   Skill Creation API
Phase 3   LLM Skill Extraction
Phase 4   Skill Validation + Verification
Phase 5   Embeddings + pgvector
Phase 6   Semantic Skill Retrieval
Phase 7   Skill Application Tracking
Phase 8   Correction Handling
Phase 9   Skill Updating
Phase 10  Skill Versioning
Phase 11  Re-index Updated Skills
Phase 12  Full AI Agent Integration
```

The Review 1 implementation should establish the foundation for these later phases without attempting to complete all of them.
