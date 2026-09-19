"""
conftest.py — pytest fixtures shared across the TeachMind test suite.

The session-scoped ``clean_test_skills`` fixture removes skills belonging to
acceptance-test users (u_acc_*) before each test session so that tests 2–5
always start from a known-clean database state and version numbers are
deterministic.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session", autouse=True)
def clean_test_skills():
    """Delete all skills owned by acceptance-test users before the session."""
    from backend.db.database import SessionLocal
    from backend.models.skill import Skill, SkillVersion

    TEST_USER_PREFIX = "u_acc_"

    db = SessionLocal()
    try:
        # Find skills whose skill_id starts with 'skill_u_acc_'
        skills = (
            db.query(Skill)
            .filter(Skill.skill_id.like(f"skill_{TEST_USER_PREFIX}%"))
            .all()
        )
        for skill in skills:
            # Delete associated version snapshots first (FK constraint)
            db.query(SkillVersion).filter(
                SkillVersion.skill_id == skill.skill_id
            ).delete(synchronize_session=False)
            db.delete(skill)
        db.commit()
    finally:
        db.close()

    yield  # run the tests

    # Optional: leave DB clean after the session too
    db = SessionLocal()
    try:
        skills = (
            db.query(Skill)
            .filter(Skill.skill_id.like(f"skill_{TEST_USER_PREFIX}%"))
            .all()
        )
        for skill in skills:
            db.query(SkillVersion).filter(
                SkillVersion.skill_id == skill.skill_id
            ).delete(synchronize_session=False)
            db.delete(skill)
        db.commit()
    finally:
        db.close()
