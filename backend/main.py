"""TeachMind Skill-Memory — FastAPI application entry-point.

Start with:

    uvicorn backend.main:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.skills import router as skills_router
from backend.db.migrations import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run database migrations on startup."""
    run_migrations()
    yield


app = FastAPI(
    title="TeachMind Skill Memory",
    description=(
        "Skill-Memory subsystem for TeachMind Review 1.  "
        "Stores, retrieves, corrects, and versions learned skills.  "
        "Provides semantic retrieval via pgvector."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# Allow the Agent / frontend (different port) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills_router)
