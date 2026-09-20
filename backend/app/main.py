"""
FastAPI Main Application for TeachMind.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.agent import router as agent_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="TeachMind — A Teachable Personalized AI Agent That Learns How You Work"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(agent_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api")  # Compatibility route


@app.get("/")
@app.get("/health")
def health_check():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
