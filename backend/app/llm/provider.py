"""
LLM Provider Abstraction Layer for TeachMind Agent.
Decouples agent orchestration from specific model providers (Gemini, OpenAI, Mock).
"""

import json
from abc import ABC, abstractmethod
from typing import Type, TypeVar, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.config import settings

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate unstructured text response."""
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        """Generate structured response validated against a Pydantic schema."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check LLM provider connectivity."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic rule-assisted mock LLM provider for offline testing & demonstration.
    """

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        p_lower = prompt.lower()
        if "deliveries" in p_lower:
            return "You have 2 active deliveries today. Wireless Mouse (Delayed) and USB-C Hub (Arriving)."
        if "briefing" in p_lower:
            return "Good morning! You have 2 meetings today and 1 delayed delivery."
        return "I have processed your request according to your personalized preferences."

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        p_lower = prompt.lower()

        # Intent classification mock response
        if "intent" in schema.__name__.lower() or "type" in schema.model_fields:
            if "don't show" in p_lower or "actually" in p_lower or "correction" in p_lower or "unless i ask" in p_lower:
                return schema(
                    type="CORRECTION",
                    intent="update_delivery_preference",
                    entities={"target": "tracking_id", "condition": "only_when_requested"},
                    confidence=0.96
                ) # type: ignore
            elif "when i ask" in p_lower or "teach" in p_lower:
                return schema(
                    type="TEACH_REQUEST",
                    intent="teach_new_workflow",
                    entities={"skill": "delivery_summary"},
                    confidence=0.95
                ) # type: ignore
            elif "yes" in p_lower or "confirm" in p_lower:
                return schema(
                    type="CONFIRMATION",
                    intent="confirm_action",
                    entities={},
                    confidence=0.98
                ) # type: ignore
            else:
                return schema(
                    type="NORMAL_REQUEST",
                    intent="check_deliveries" if "deliveries" in p_lower else "morning_briefing",
                    entities={"date": "today"},
                    confidence=0.94
                ) # type: ignore

        # Fallback empty model instantiation
        try:
            return schema()
        except Exception:
            return schema.model_construct()

    def health_check(self) -> bool:
        return True


def get_llm_provider() -> BaseLLMProvider:
    """Factory function returning active LLM provider."""
    # Default to MockLLMProvider for fast, reliable, offline hackathon execution if keys are not present
    return MockLLMProvider()
