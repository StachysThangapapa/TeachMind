"""Database migration script — creates pgvector extension and all tables.

Run once before first application start:

    python -m backend.db.migrations
"""

from sqlalchemy import text

from backend.db.database import Base, engine

# Import models so they are registered on Base.metadata before create_all().
from backend.models.skill import Skill, SkillVersion  # noqa: F401


def run_migrations() -> None:
    """Enable pgvector and create all tables defined in ORM models."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    print("Migrations complete — pgvector enabled, tables created.")


if __name__ == "__main__":
    run_migrations()
