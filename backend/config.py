"""Application settings loaded from environment variables / .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Skill-Memory configuration.

    All values can be overridden via environment variables or a .env file
    placed in the project root.
    """

    database_url: str = "postgresql://postgres:postgres@localhost:5432/teachmind"
    cohere_api_key: str = ""
    embedding_model: str = "embed-english-light-v3.0"
    embedding_dimension: int = 384
    extraction_model: str = "command-r-08-2024"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
