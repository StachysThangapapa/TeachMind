"""
TeachMind Verification Package.
Provides verification metrics, test case loaders, and evaluators.
"""

from backend.verification.metrics import calculate_accuracy
from backend.verification.evaluator import SkillEvaluator
from backend.verification.test_cases import TestCaseLoader

__all__ = [
    "calculate_accuracy",
    "SkillEvaluator",
    "TestCaseLoader",
]
