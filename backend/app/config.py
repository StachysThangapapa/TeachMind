"""
Configuration and settings module for TeachMind Backend.
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "TeachMind AI Agent"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SKILL_MATCH_THRESHOLD: float = float(os.getenv("SKILL_MATCH_THRESHOLD", "0.75"))
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_USER_ID: str = "user_default"


settings = Settings()
