"""SQLAlchemy engine, session factory, and declarative base with resilient fallback."""

import logging
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def _init_engine():
    """Initializes database engine with automatic local SQLite fallback if PostgreSQL is unreachable."""
    db_url = settings.database_url

    engine_instance = None
    if "postgresql" in db_url:
        try:
            # Test PostgreSQL connectivity with a short timeout
            test_engine = create_engine(db_url, connect_args={"connect_timeout": 3}, pool_pre_ping=True)
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info(f"[Database] Successfully connected to PostgreSQL: {db_url}")
            engine_instance = test_engine
        except Exception as e:
            logger.warning(
                f"[Database Warning] PostgreSQL connection to '{db_url}' failed ({e}). "
                "Falling back to local SQLite database (sqlite:///backend/app/data/teachmind.db) "
                "so the application runs out-of-the-box."
            )
            data_dir = Path(__file__).parent.parent / "app" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            sqlite_path = data_dir / "teachmind.db"
            fallback_url = f"sqlite:///{sqlite_path}"
            engine_instance = create_engine(
                fallback_url,
                echo=False,
                connect_args={"check_same_thread": False},
                pool_pre_ping=True
            )
    else:
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        engine_instance = create_engine(db_url, echo=False, connect_args=connect_args, pool_pre_ping=True)

    # Ensure tables are created automatically
    try:
        from backend.models.skill import Skill, SkillVersion  # noqa: F401
        Base.metadata.create_all(bind=engine_instance)
    except Exception as e:
        logger.warning(f"[Database Warning] Auto table creation: {e}")

    return engine_instance


engine = _init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency — yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
