"""Database migration script — creates pgvector extension and all tables.

Run once before first application start:

    python -m backend.db.migrations
"""

import logging
from sqlalchemy import text

from backend.db.database import Base, engine
from backend.models.skill import Skill, SkillVersion  # noqa: F401

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Enable pgvector and create all tables defined in ORM models."""
    try:
        with engine.connect() as conn:
            if "postgresql" in str(engine.url):
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    logger.info("[Migrations] pgvector extension enabled.")
                except Exception as e:
                    logger.warning(f"[Migrations Warning] Could not enable pgvector extension: {e}")

        Base.metadata.create_all(bind=engine)
        logger.info("[Migrations] Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"[Migrations Error] Database initialization failed: {e}")


if __name__ == "__main__":
    run_migrations()
