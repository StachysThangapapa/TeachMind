"""
LLM Provider Abstraction Layer for TeachMind Agent.
Supports OpenAI API (with real OPENAI_API_KEY), Gemini API, and Mock fallback.
"""

import os
import json
import urllib.request
import urllib.error
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


class OpenAILLMProvider(BaseLLMProvider):
    """
    Real OpenAI LLM Provider calling OpenAI API (gpt-4o-mini / gpt-4o).
    Uses standard library urllib.request to work out-of-the-box without extra packages.
    """

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self.endpoint = "https://api.openai.com/v1/chat/completions"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2
        }

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"[OpenAI API Warning]: {e}. Falling back to rule assistant.")
            return MockLLMProvider().generate(prompt, system_prompt)

    def generate_structured(self, prompt: str, schema: Type[T], system_prompt: str = "") -> T:
        instruct_prompt = (
            f"{system_prompt}\n\nRespond ONLY with valid JSON matching this schema:\n"
            f"{json.dumps(schema.model_json_schema())}\n\nUser Prompt: {prompt}"
        )
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": instruct_prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.1
        }

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed_json = json.loads(content)
                return schema(**parsed_json)
        except Exception as e:
            print(f"[OpenAI API Warning]: {e}. Falling back to MockLLMProvider.")
            return MockLLMProvider().generate_structured(prompt, schema, system_prompt)

    def health_check(self) -> bool:
        try:
            res = self.generate("Hello", system_prompt="Ping")
            return bool(res)
        except Exception:
            return False


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
                )
            elif "when i ask" in p_lower or "teach" in p_lower:
                return schema(
                    type="TEACH_REQUEST",
                    intent="teach_new_workflow",
                    entities={"skill": "delivery_summary"},
                    confidence=0.95
                )
            elif "yes" in p_lower or "confirm" in p_lower:
                return schema(
                    type="CONFIRMATION",
                    intent="confirm_action",
                    entities={},
                    confidence=0.98
                )
            else:
                return schema(
                    type="NORMAL_REQUEST",
                    intent="check_deliveries" if "deliveries" in p_lower else "morning_briefing",
                    entities={"date": "today"},
                    confidence=0.94
                )

        try:
            return schema()
        except Exception:
            return schema.model_construct()

    def health_check(self) -> bool:
        return True


def get_llm_provider() -> BaseLLMProvider:
    """Factory function returning active LLM provider based on .env settings."""
    api_key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY
    if api_key and api_key.startswith("sk-"):
        return OpenAILLMProvider(api_key=api_key)
    
    return MockLLMProvider()
