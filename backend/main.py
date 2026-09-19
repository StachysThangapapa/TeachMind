"""
TeachMind Application Entrypoint.
Re-exports the FastAPI app from backend.app.main.
"""

from backend.app.main import app, lifespan

__all__ = ["app", "lifespan"]
