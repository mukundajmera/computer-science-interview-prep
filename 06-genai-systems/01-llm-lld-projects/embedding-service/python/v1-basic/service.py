"""
Embedding service orchestrator.

:class:`EmbeddingService` ties together an :class:`EmbeddingModel`,
an optional :class:`EmbeddingCache`, input validation, and L2
normalization into a single cohesive API.
"""

import math
from typing import List, Optional

from embedding_model import EmbeddingModel, EmbeddingResult
from cache import EmbeddingCache


class EmbeddingService:
    """High-level embedding service combining model, cache, and normalization.

    Args:
        model: The embedding model backend to use.
        cache: Optional cache for storing computed embeddings.
    """

    def __init__(
        self,
        model: EmbeddingModel,
        cache: Optional[EmbeddingCache] = None,
    ) -> None:
        self._model = model
        self._cache = cache
        self._total_embeddings = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed(self, text: str) -> EmbeddingResult:
        """Generate a normalised embedding for *text*.

        Args:
            text: Non-empty input string.

        Returns:
            An :class:`EmbeddingResult` containing the embedding vector.

        Raises:
            ValueError: If *text* is empty or whitespace-only.
        """
        self._validate_text(text)

        cache_key = self._cache_key(text)

        # Cache lookup
        if self._cache is not None:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._total_embeddings += 1
                return EmbeddingResult(
                    text=text,
                    embedding=cached,
                    model_name=self._model.model_name,
                    dimensions=self._model.dimensions,
                    cached=True,
                )

        # Compute and normalise
        raw = self._model.embed(text)
        normalised = self.normalize_embedding(raw)

        # Store in cache
        if self._cache is not None:
            self._cache.put(cache_key, normalised)

        self._total_embeddings += 1
        return EmbeddingResult(
            text=text,
            embedding=normalised,
            model_name=self._model.model_name,
            dimensions=self._model.dimensions,
            cached=False,
        )

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate normalised embeddings for multiple texts.

        Each text is processed individually, benefiting from the cache
        for any repeated inputs.

        Args:
            texts: List of non-empty input strings.

        Returns:
            A list of :class:`EmbeddingResult` objects.

        Raises:
            ValueError: If any text is empty or whitespace-only.
        """
        return [self.embed(t) for t in texts]

    @staticmethod
    def normalize_embedding(embedding: List[float]) -> List[float]:
        """L2-normalise an embedding vector to unit length.

        If the vector has zero magnitude, it is returned unchanged.

        Args:
            embedding: Raw embedding vector.

        Returns:
            A new list of floats with L2 norm ≈ 1.0.
        """
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude == 0.0:
            return list(embedding)
        return [x / magnitude for x in embedding]

    def get_stats(self) -> dict:
        """Return operational metrics.

        Returns:
            A dict with model info, total embeddings, and cache stats.
        """
        stats: dict = {
            "model": self._model.model_name,
            "dimensions": self._model.dimensions,
            "total_embeddings": self._total_embeddings,
        }
        if self._cache is not None:
            stats["cache"] = self._cache.stats()
        return stats

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_text(self, text: str) -> None:
        """Raise ``ValueError`` for empty or whitespace-only text."""
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")

    def _cache_key(self, text: str) -> str:
        """Derive a cache key from model name and text content."""
        return f"{self._model.model_name}:{text}"
