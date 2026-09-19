"""Embedding generation abstraction.

Provides:
  - ``EmbeddingProvider``  — abstract interface (swap implementations freely)
  - ``CohereEmbeddingProvider`` — concrete Cohere implementation
  - ``DeterministicFallbackEmbeddingProvider`` — deterministic local fallback
  - ``get_embedding_provider`` — factory function choosing provider based on configuration
  - ``build_embedding_text`` — builds the text fed to the embedding model
"""

from __future__ import annotations

import hashlib
import logging
import math
from abc import ABC, abstractmethod
from typing import List, Optional

from backend.config import settings

logger = logging.getLogger(__name__)


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
        import cohere

        self._api_key = api_key or settings.cohere_api_key
        if not self._api_key:
            raise ValueError("Cohere API key is not configured.")
        self._client = cohere.ClientV2(api_key=self._api_key)
        self._model = model or settings.embedding_model
        logger.info(f"[EmbeddingProvider] Using production CohereEmbeddingProvider with model: {self._model}")

    def embed_document(self, text: str) -> List[float]:
        return self._embed(text, input_type="search_document")

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text, input_type="search_query")

    def _embed(self, text: str, input_type: str) -> List[float]:
        response = self._client.embed(
            texts=[text],
            model=self._model,
            input_type=input_type,
            embedding_types=["float"],
        )
        return list(response.embeddings.float[0])


# ── Deterministic local fallback ───────────────────────────────────────


class DeterministicFallbackEmbeddingProvider(EmbeddingProvider):
    """Deterministic local embedding provider when Cohere API key is unavailable.

    Generates normalized 384-dimensional vectors using token hash distributions.
    Allows local development and automated testing without external network dependencies.
    """

    def __init__(self, dimension: int = 384) -> None:
        self._dim = dimension
        logger.info(f"[EmbeddingProvider] Using DeterministicFallbackEmbeddingProvider (dim={self._dim}).")

    def _hash_vector(self, text: str) -> List[float]:
        vec = [0.0] * self._dim
        import re
        words = re.findall(r"\w+", text.lower())
        if not words:
            words = ["empty"]

        for word in words:
            # Hash each word consistently across docs and queries
            h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
            idx = h % self._dim
            vec[idx] += 1.0

        # Normalize to unit length for cosine similarity
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec

    def embed_document(self, text: str) -> List[float]:
        return self._hash_vector(text)

    def embed_query(self, text: str) -> List[float]:
        return self._hash_vector(text)



def get_default_embedding_provider() -> EmbeddingProvider:
    """Factory creating Cohere provider if API key present, else local fallback."""
    if settings.cohere_api_key and not settings.cohere_api_key.startswith("your-"):
        try:
            return CohereEmbeddingProvider()
        except Exception as e:
            logger.warning(f"[EmbeddingProvider Warning] Failed initializing Cohere provider ({e}). Falling back to local deterministic embedding.")
            return DeterministicFallbackEmbeddingProvider(settings.embedding_dimension)
    return DeterministicFallbackEmbeddingProvider(settings.embedding_dimension)


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
            instr = s.get("instruction", "") if isinstance(s, dict) else getattr(s, "instruction", "")
            if instr:
                parts.append(instr)

    rules = skill_data.get("rules") or []
    if rules:
        parts.append("Rules:")
        for r in rules:
            if isinstance(r, dict):
                parts.append(f"If {r.get('condition', '')}, then {r.get('action', '')}")
            else:
                parts.append(f"If {getattr(r, 'condition', '')}, then {getattr(r, 'action', '')}")

    examples = skill_data.get("examples") or []
    if examples:
        parts.append("Examples:")
        for e in examples:
            if isinstance(e, dict):
                parts.append(
                    f"Input: {e.get('input', '')} → {e.get('expected_behavior', '')}"
                )
            else:
                parts.append(f"Input: {getattr(e, 'input', '')} → {getattr(e, 'expected_behavior', '')}")

    return "\n".join(parts)
