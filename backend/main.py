"""TeachMind Skill-Memory — FastAPI application entry-point.

Start with:

    uvicorn backend.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.skills import router as skills_router
from backend.app.api.agent import router as agent_router
from backend.db.migrations import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run database migrations on startup."""
    run_migrations()
    yield


app = FastAPI(
    title="TeachMind Unified Backend",
    description=(
        "Unified backend for TeachMind. "
        "Provides Skill-Memory with PostgreSQL + pgvector + Cohere embeddings, "
        "Cohere natural-language Skill Extraction, "
        "and the AI Agent orchestration layer."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Allow the frontend and subagent clients to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Skill Memory and Extraction endpoints (/skills, /skills/search, /skills/extract, etc.)
app.include_router(skills_router)

# AI Agent endpoints (/agent/execute, /agent/chat, /agent/teach, etc.)
app.include_router(agent_router)
app.include_router(agent_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api")


@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "project": "TeachMind Unified System",
        "version": "1.0.0",
        "subsystems": {
            "skill_memory": "active",
            "cohere_extraction": "active",
            "ai_agent": "active",
            "verification": "active"
        }
    }
