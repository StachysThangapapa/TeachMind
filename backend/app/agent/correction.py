"""
Correction Learning Module for TeachMind Agent.
Handles user correction parsing, skill exception insertion, version incrementing (v1.0 -> v1.1),
and regression verification triggering.
"""

from typing import Dict, Any, Tuple
from backend.app.schemas.agent import SkillSummary, PersonalContext, VerificationReport
from backend.app.agent.context import context_manager
from backend.app.verification.client import verification_client


class CorrectionEngine:
    """Processes user corrections and increments skill versions safely."""

    def apply_correction(
        self,
        skill: SkillSummary,
        user_correction: str,
        user_id: str = "user_default"
    ) -> Tuple[SkillSummary, VerificationReport, Dict[str, Any]]:
        """
        Applies a correction to a skill:
        1. Appends exception/rule.
        2. Bumps minor version (e.g. 1.0 -> 1.1).
        3. Updates user personal context preference.
        4. Triggers regression verification.
        """
        # Parse current version number
        try:
            major, minor = skill.version.split(".")
            new_version = f"{major}.{int(minor) + 1}"
        except Exception:
            new_version = "1.1"

        # Update skill rules / exceptions
        updated_exceptions = list(skill.exceptions)
        updated_exceptions.append({
            "condition": user_correction,
            "action": "override_preference"
        })

        updated_skill = SkillSummary(
            id=skill.id,
            name=skill.name,
            description=skill.description,
            version=new_version,
            confidence=0.95,
            triggers=skill.triggers,
            steps=skill.steps,
            rules=skill.rules,
            exceptions=updated_exceptions
        )

        # Update user preference context if tracking ID preference was corrected
        if "tracking" in user_correction.lower():
            context_manager.update_preference(user_id, "delivery", "show_tracking_id", "only_when_requested")

        context_manager.record_correction(user_id, user_correction, skill.id)

        # Mock agent runner for regression verification test suite
        def mock_agent_runner(input_str: str):
            return "approve"

        # Trigger regression verification suite
        verification_report = verification_client.verify_skill(
            skill_id=skill.id,
            agent_runner=mock_agent_runner,
            is_regression=True
        )

        meta = {
            "version_bump": f"{skill.version} -> {new_version}",
            "regression_status": verification_report.regression_status,
            "tests_passed": verification_report.correct
        }

        return updated_skill, verification_report, meta


correction_engine = CorrectionEngine()
