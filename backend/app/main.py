"""
FastAPI Main Application for TeachMind.
Integrates AI Agent endpoints with persistent Skill Memory subsystem.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.migrations import run_migrations
from backend.api.skills import router as skills_router
from backend.app.api.agent import router as agent_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run database migrations and initialize schema on startup."""
    run_migrations()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="TeachMind — A Teachable Personalized AI Agent That Learns How You Work",
    lifespan=lifespan,
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Skill-Memory REST Endpoints (/skills, /skills/search, etc.)
app.include_router(skills_router)

# Mount AI Agent Endpoints (/api/v1/agent, /api/agent, /agent)
app.include_router(agent_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api")
app.include_router(agent_router, prefix="")


@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
