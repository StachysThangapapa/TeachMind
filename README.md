# TeachMind

A teachable AI assistant that learns how you work.

## Skill-Memory Subsystem (Review 1)

The Skill-Memory backend stores, retrieves, corrects, and versions learned skills using PostgreSQL + pgvector for semantic retrieval.

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+** with the [pgvector](https://github.com/pgvector/pgvector) extension installed
- **Cohere API key** (for embedding generation)

### Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create the PostgreSQL database
psql -U postgres -c "CREATE DATABASE teachmind;"

# 4. Configure environment
copy .env.example .env
# Edit .env — set your COHERE_API_KEY and DATABASE_URL

# 5. Run migrations (creates pgvector extension + tables)
python -m backend.db.migrations

# 6. Seed sample skills (optional — requires Cohere API key)
python -m scripts.seed_skills

# 7. Start the server
uvicorn backend.main:app --reload --port 8000
```

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/skills` | Store a new skill |
| `POST` | `/skills/search` | Semantic skill retrieval |
| `GET` | `/skills` | List all skills (summaries) |
| `GET` | `/skills/{skill_id}` | Get a single skill |
| `PATCH` | `/skills/{skill_id}` | Correct / update a skill |
| `PATCH` | `/skills/{skill_id}/verify` | Mark a skill as verified |
| `GET` | `/skills/{skill_id}/versions` | View version history |

Interactive API docs available at: `http://localhost:8000/docs`

### Testing

```bash
# Store a skill
curl -X POST http://localhost:8000/skills \
  -H "Content-Type: application/json" \
  -d '{"skill_id":"test_001","name":"Test Skill","description":"A test skill.","triggers":["test trigger"],"steps":[{"step":1,"instruction":"Do the thing."}],"rules":[],"examples":[],"version":1,"verified":false}'

# Search (semantic)
curl -X POST http://localhost:8000/skills/search \
  -H "Content-Type: application/json" \
  -d '{"query":"Can you make this months sales report?","top_k":3}'

# List
curl http://localhost:8000/skills

# Get one
curl http://localhost:8000/skills/test_001

# Correct
curl -X PATCH http://localhost:8000/skills/test_001 \
  -H "Content-Type: application/json" \
  -d '{"steps":[{"step":1,"instruction":"Updated instruction."}]}'

# Verify
curl -X PATCH http://localhost:8000/skills/test_001/verify

# Version history
curl http://localhost:8000/skills/test_001/versions
```

### Architecture

```
backend/
├── api/
│   └── skills.py               # FastAPI router (all /skills endpoints)
├── db/
│   ├── database.py             # SQLAlchemy engine + session
│   └── migrations.py           # Schema creation (pgvector + tables)
├── models/
│   └── skill.py                # SQLAlchemy ORM models (skills, skill_versions)
├── schemas/
│   └── skill.py                # Pydantic request/response models
├── services/
│   ├── embedding_service.py    # Abstract embedding provider + Cohere impl
│   └── skill_service.py        # Business logic layer
├── repositories/
│   └── skill_repository.py     # Database access layer
├── config.py                   # Application settings
└── main.py                     # FastAPI application entry-point
```

### Integration Notes for Agent Teammate

The Agent should call:

```
POST /skills/search
{"query": "<user's current task>", "top_k": 3}
```

The response is machine-readable canonical Skill JSON — see `docs/struct.json` for the exact contract.

To send corrections after execution/verification:

```
PATCH /skills/{skill_id}
{"steps": [...corrected steps...]}
```

Then to mark as verified:

```
PATCH /skills/{skill_id}/verify
```
