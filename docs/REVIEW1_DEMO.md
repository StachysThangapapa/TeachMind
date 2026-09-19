# TeachMind — Review 1 Demonstration

## 1. Component Overview

### My contribution: Skill Memory

The Skill Memory subsystem is my component within TeachMind. It is responsible for storing, retrieving, correcting, and versioning the workflows that a user teaches to the system.

### System boundary

```
User
  ↓
Skill/Action Extraction       ← separate component (not mine)
  ↓
Canonical Skill JSON
  ↓
Skill Memory                  ← MY COMPONENT
  ↓
PostgreSQL + pgvector
  ↓
Retrieved Skill JSON
  ↓
AI Agent                      ← separate component (not mine)
  ↓
Execution
```

### What Skill Memory does

- Validates incoming canonical Skill JSON
- Stores skills persistently in PostgreSQL
- Generates and stores vector embeddings (Cohere embed-english-light-v3.0, 384 dimensions)
- Performs semantic retrieval using pgvector cosine similarity
- Supports partial corrections to stored skills
- Maintains version history (corrections do not destroy previous versions)
- Maintains verification status

### What Skill Memory does NOT do

- Agent reasoning or planning
- Desktop action planning or execution
- Skill/action extraction from user instructions
- General application orchestration

---

## 2. Demonstration Flow

All steps are performed through the Swagger UI at `http://localhost:8000/docs`.

### Step 1 — Store a skill

**Endpoint:** `POST /skills`

Paste the following body:

```json
{
  "skill_id": "skill_002",
  "name": "Process Monthly Report",
  "description": "Create a monthly Excel report from a sales CSV.",
  "triggers": [
    "prepare monthly report",
    "create monthly sales report",
    "generate sales report"
  ],
  "steps": [
    {"step": 1, "instruction": "Use the provided sales CSV as the input."},
    {"step": 2, "instruction": "Create an Excel report."},
    {"step": 3, "instruction": "Add a summary sheet."},
    {"step": 4, "instruction": "Add a chart."},
    {"step": 5, "instruction": "Save the completed report."}
  ],
  "rules": [],
  "examples": [
    {
      "input": "Here is this month's sales data, make my report.",
      "expected_behavior": "An Excel file with summary sheet and chart is saved to Reports."
    }
  ],
  "version": 1,
  "verified": false
}
```

**Expected result:** HTTP 201 with the full canonical Skill JSON response including server-generated `metadata.created_at` and `metadata.updated_at`.

### Step 2 — Semantic search with different wording

**Endpoint:** `POST /skills/search`

Paste the following body:

```json
{
  "query": "Generate this month's report",
  "top_k": 3
}
```

**What this demonstrates:** The query `"Generate this month's report"` uses completely different wording from the stored skill's name (`"Process Monthly Report"`) and its triggers. The system retrieves the correct skill because the search uses vector similarity, not keyword matching.

**Expected result:** HTTP 200. The response contains `skill_002` with a similarity score, and the nested `skill` object contains the complete canonical Skill JSON.

### Step 3 — Correct the skill

**Endpoint:** `PATCH /skills/skill_002`

Paste the following body:

```json
{
  "steps": [
    {"step": 1, "instruction": "Use the provided sales CSV as the input."},
    {"step": 2, "instruction": "Create an Excel report."},
    {"step": 3, "instruction": "Add a summary sheet."},
    {"step": 4, "instruction": "Add a chart."},
    {"step": 5, "instruction": "Save the completed report as a PDF."}
  ]
}
```

**What this demonstrates:** Step 5 has been corrected from `"Save the completed report."` to `"Save the completed report as a PDF."` The system automatically increments the version to 2, regenerates the embedding to reflect the updated content, and saves the previous version to the history table.

**Expected result:** HTTP 200. Response shows `"version": 2` and the updated step 5.

### Step 4 — View version history

**Endpoint:** `GET /skills/skill_002/versions`

**What this demonstrates:** Both version 1 (original) and version 2 (corrected) are returned. The correction did not destroy the previous version.

**Expected result:** HTTP 200. An array with two entries: version 1 with the original step 5, and version 2 with the corrected step 5.

### Step 5 — Verify the skill

**Endpoint:** `PATCH /skills/skill_002/verify`

No request body required.

**What this demonstrates:** After the user confirms that the corrected skill works correctly, the skill is marked as verified. This does not change any other fields.

**Expected result:** HTTP 200. Response shows `"verified": true`.

---

## 3. What Each Test Proves

| API | Purpose | What it proves |
|-----|---------|----------------|
| `POST /skills` | Store a learned skill | Persistent skill storage with embedding generation |
| `POST /skills/search` | Semantic retrieval | A differently worded request retrieves the relevant skill |
| `PATCH /skills/{skill_id}` | Correction | A learned skill can be updated without losing history |
| `GET /skills/{skill_id}/versions` | Version history | Previous versions are preserved after correction |
| `PATCH /skills/{skill_id}/verify` | Verification | Skill verification state is maintained independently |

---

## 4. Technical Explanation

### Semantic search pipeline

```
User request (natural language)
  ↓
Cohere embed-english-light-v3.0 (input_type="search_query")
  ↓
384-dimensional query vector
  ↓
pgvector cosine similarity search (SQL: embedding <=> query_vector)
  ↓
Results ranked by similarity (1 − cosine distance)
  ↓
Top-k results returned
  ↓
Each result contains the complete canonical Skill JSON
```

The similarity ranking does not use an LLM. It uses vector distance computed directly by pgvector inside PostgreSQL. The embedding model converts text to vectors; pgvector compares those vectors mathematically.

When a skill is stored, the embedding is generated with `input_type="search_document"`. When a search query arrives, the embedding is generated with `input_type="search_query"`. This asymmetric approach is how Cohere's v3 embedding models are designed to be used for retrieval.

### Versioning

```
Version 1 (initial skill)
  ↓ correction
Version 2 (updated steps, new embedding)
  ↓ correction
Version 3 (further updates, new embedding)
```

The `skills` table always holds the current/latest version. This is the version used for search and normal retrieval.

The `skill_versions` table stores an immutable snapshot of every version. When a correction is applied, the service increments the version number, updates the `skills` row, regenerates the embedding, and appends the new state to `skill_versions`. Previous version rows are never modified or deleted.

### Embedding provider abstraction

The embedding logic is behind an abstract `EmbeddingProvider` interface. The current implementation uses Cohere, but the provider can be swapped without changing any business logic or database code.

---

## 5. Reviewer Talking Points

> My contribution is the Skill Memory subsystem of TeachMind. Its purpose is to give the agent persistent memory of workflows that the user has taught it.
>
> When the upstream extraction component produces a canonical Skill JSON — which contains the skill name, description, triggers, ordered steps, conditional rules, and examples — Skill Memory validates that JSON, generates a vector embedding using Cohere's embedding model, and stores both the skill data and the embedding in PostgreSQL with pgvector.
>
> When the user later asks for help with a task, the agent sends a natural-language query to Skill Memory. Skill Memory converts that query into a vector and uses pgvector to find the most similar stored skills by cosine distance. This is pure vector math, not an LLM call. The result is a ranked list of skills in canonical JSON format that the agent can then execute.
>
> The system also supports corrections. If the user teaches a skill and then says "actually, save it as a PDF instead," the correction updates the current skill, regenerates the embedding so future searches reflect the change, and preserves the previous version in a history table. Nothing is lost.
>
> There is also a verification endpoint. After the agent executes a skill and the user confirms it worked correctly, the skill is marked as verified.
>
> My component is strictly the storage and retrieval layer. It does not do agent reasoning, it does not plan desktop actions, and it does not execute anything. It receives canonical JSON in, stores it with an embedding, and returns canonical JSON out.

---

## 6. Demo Result

**Core success criterion:**

TeachMind can remember a workflow taught by the user and retrieve that workflow when the user later asks for a related task using different wording.

This is demonstrated by:

1. Storing `"Process Monthly Report"` as a skill.
2. Searching with `"Generate this month's report"` — different words, same intent.
3. The system returns the stored skill with a high similarity score.

The retrieval works because the system uses semantic vector similarity, not keyword matching.

---

## 7. Architecture Reference

```
backend/
├── api/
│   └── skills.py               # FastAPI router — 7 endpoints
├── db/
│   ├── database.py             # SQLAlchemy engine + session
│   └── migrations.py           # pgvector extension + table creation
├── models/
│   └── skill.py                # ORM: skills table + skill_versions table
├── schemas/
│   └── skill.py                # Pydantic request/response models
├── services/
│   ├── embedding_service.py    # Abstract EmbeddingProvider + Cohere impl
│   └── skill_service.py        # Business logic (store, search, correct, verify)
├── repositories/
│   └── skill_repository.py     # Database access layer + pgvector queries
├── config.py                   # Settings (DB URL, Cohere key, model, dimension)
└── main.py                     # FastAPI app entry point
```

**Database tables:**

| Table | Purpose |
|-------|---------|
| `skills` | Current/latest version of each skill. Contains the pgvector embedding column. Searched during retrieval. |
| `skill_versions` | Append-only history. One row per version per skill. No embedding (not searched directly). |
