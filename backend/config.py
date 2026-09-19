"""Application settings loaded from environment variables / .env file."""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Unified configuration for TeachMind."""

    PROJECT_NAME: str = "TeachMind AI Agent & Skill Memory"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    SKILL_MATCH_THRESHOLD: float = 0.75
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    DEFAULT_USER_ID: str = "user_default"

    # Skill-Memory / Database settings
    database_url: str = "postgresql://postgres:postgres@localhost:5432/teachmind"
    cohere_api_key: str = ""
    embedding_model: str = "embed-english-light-v3.0"
    embedding_dimension: int = 384

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()
