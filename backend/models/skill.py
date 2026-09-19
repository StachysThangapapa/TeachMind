"""SQLAlchemy ORM models for Skill Memory.

Tables
------
skills          – current/latest version of each skill (searched via pgvector)
skill_versions  – append-only history of every version a skill has had
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Text,
    JSON,
    UniqueConstraint,
    func,
)
from pgvector.sqlalchemy import Vector

from backend.config import settings
from backend.db.database import Base


class Skill(Base):
    """Current/active version of a stored skill.

    This is the table searched by pgvector for semantic retrieval.
    """

    __tablename__ = "skills"

    skill_id = Column(Text, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False, default="")
    triggers = Column(JSON, nullable=False, default=list)
    steps = Column(JSON, nullable=False, default=list)
    rules = Column(JSON, nullable=False, default=list)
    examples = Column(JSON, nullable=False, default=list)
    version = Column(Integer, nullable=False, default=1)
    verified = Column(Boolean, nullable=False, default=False)
    embedding = Column(Vector(settings.embedding_dimension), nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class SkillVersion(Base):
    """Immutable snapshot of a skill at a particular version.

    A new row is appended every time a skill is stored or corrected.
    This preserves the full correction history without overwriting data.
    """

    __tablename__ = "skill_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(Text, nullable=False, index=True)
    version = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False, default="")
    triggers = Column(JSON, nullable=False, default=list)
    steps = Column(JSON, nullable=False, default=list)
    rules = Column(JSON, nullable=False, default=list)
    examples = Column(JSON, nullable=False, default=list)
    verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    __table_args__ = (
        UniqueConstraint("skill_id", "version", name="uq_skill_version"),
    )
