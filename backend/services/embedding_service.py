"""Embedding generation abstraction.

Provides:
  - ``EmbeddingProvider``  — abstract interface (swap implementations freely)
  - ``CohereEmbeddingProvider`` — concrete Cohere implementation (default)
  - ``build_embedding_text`` — builds the text fed to the embedding model

The Skill-Memory subsystem calls only the abstract interface.  The concrete
provider is injected via FastAPI dependency injection so it can be replaced
without touching business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

import cohere

from backend.config import settings


# ── Abstract interface ─────────────────────────────────────────────────


class EmbeddingProvider(ABC):
    """Provider-agnostic embedding interface."""

    @abstractmethod
    def embed_document(self, text: str) -> List[float]:
        """Generate an embedding for a skill document being stored."""
        ...

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Generate an embedding for a search query."""
        ...


# ── Cohere implementation ──────────────────────────────────────────────


class CohereEmbeddingProvider(EmbeddingProvider):
    """Cohere embed-english-light-v3.0 (384-dim) embedding provider.

    Uses ``input_type="search_document"`` for stored skills and
    ``input_type="search_query"`` for search queries so the asymmetric
    retrieval model works correctly.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self._client = cohere.ClientV2(
            api_key=api_key or settings.cohere_api_key,
        )
        self._model = model or settings.embedding_model

    # ── public API ─────────────────────────────────────────────────

    def embed_document(self, text: str) -> List[float]:
        return self._embed(text, input_type="search_document")

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text, input_type="search_query")

    # ── internal ───────────────────────────────────────────────────

    def _embed(self, text: str, input_type: str) -> List[float]:
        response = self._client.embed(
            texts=[text],
            model=self._model,
            input_type=input_type,
            embedding_types=["float"],
        )
        return list(response.embeddings.float[0])


# ── Text builder ───────────────────────────────────────────────────────


def build_embedding_text(skill_data: dict) -> str:
    """Build a single text block from skill fields for embedding.

    Follows the layout described in spec §8:
        Name
        Description
        Triggers: …
        Steps: …
        Rules: …
        Examples: …
    """
    parts: list[str] = []

    if name := skill_data.get("name"):
        parts.append(name)

    if desc := skill_data.get("description"):
        parts.append(desc)

    triggers = skill_data.get("triggers") or []
    if triggers:
        parts.append("Triggers:")
        parts.extend(triggers)

    steps = skill_data.get("steps") or []
    if steps:
        parts.append("Steps:")
        for s in steps:
            instr = s.get("instruction", "") if isinstance(s, dict) else s.instruction
            parts.append(instr)

    rules = skill_data.get("rules") or []
    if rules:
        parts.append("Rules:")
        for r in rules:
            if isinstance(r, dict):
                parts.append(f"If {r.get('condition', '')}, then {r.get('action', '')}")
            else:
                parts.append(f"If {r.condition}, then {r.action}")

    examples = skill_data.get("examples") or []
    if examples:
        parts.append("Examples:")
        for e in examples:
            if isinstance(e, dict):
                parts.append(
                    f"Input: {e.get('input', '')} → {e.get('expected_behavior', '')}"
                )
            else:
                parts.append(f"Input: {e.input} → {e.expected_behavior}")

    return "\n".join(parts)
