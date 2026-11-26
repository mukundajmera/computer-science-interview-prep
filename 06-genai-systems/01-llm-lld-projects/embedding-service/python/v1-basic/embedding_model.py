"""
Embedding model abstractions and stub implementations.

Defines the ``EmbeddingModel`` ABC and two concrete stubs:

* **RandomEmbeddingModel** — non-deterministic, for demos and pipeline tests.
* **HashEmbeddingModel** — deterministic via SHA-256, for repeatable unit tests.

Also provides lightweight dataclasses for request and result payloads.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
import hashlib
import random


# ---------------------------------------------------------------------------
# Data carriers
# ---------------------------------------------------------------------------

@dataclass
class EmbeddingRequest:
    """Input payload for an embedding request.

    Attributes:
        text: The text string to embed.
        model_name: Optional identifier for the target model.
    """

    text: str
    model_name: str = "default"


@dataclass
class EmbeddingResult:
    """Output payload returned by the embedding service.

    Attributes:
        text: The original input text.
        embedding: The computed dense vector.
        model_name: Which model produced the embedding.
        dimensions: Dimensionality of the embedding vector.
        cached: Whether this result was served from cache.
    """

    text: str
    embedding: List[float]
    model_name: str
    dimensions: int
    cached: bool = False


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class EmbeddingModel(ABC):
    """Strategy interface for embedding model backends.

    Subclasses must implement :meth:`embed` to convert a single text
    string into a dense vector.  The default :meth:`embed_batch`
    implementation delegates to :meth:`embed` sequentially; subclasses
    may override for optimised batch processing.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Human-readable identifier for this model."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Dimensionality of the output embeddings."""

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate an embedding vector for *text*.

        Args:
            text: Non-empty input string.

        Returns:
            A list of floats with length equal to :attr:`dimensions`.
        """

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        The default implementation calls :meth:`embed` sequentially.
        Subclasses may override for batch-optimised backends.

        Args:
            texts: List of non-empty input strings.

        Returns:
            A list of embedding vectors, one per input text.
        """
        return [self.embed(t) for t in texts]


# ---------------------------------------------------------------------------
# Concrete stubs
# ---------------------------------------------------------------------------

class RandomEmbeddingModel(EmbeddingModel):
    """Stub model that produces random embeddings.

    Useful for demonstrations and integration testing where the actual
    vector values are irrelevant.  Produces **non-deterministic** output.

    Args:
        dimensions: Number of dimensions for output vectors (default 128).
    """

    def __init__(self, dimensions: int = 128) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return "random"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> List[float]:
        """Return a random vector of :attr:`dimensions` floats in [0, 1)."""
        return [random.random() for _ in range(self._dimensions)]


class HashEmbeddingModel(EmbeddingModel):
    """Stub model that produces deterministic hash-based embeddings.

    Uses SHA-256 of the input text, expanded cyclically to fill the
    requested dimensionality.  The same text always yields the same
    embedding, making this model ideal for repeatable unit tests.

    Args:
        dimensions: Number of dimensions for output vectors (default 128).
    """

    def __init__(self, dimensions: int = 128) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be positive")
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return "hash"

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> List[float]:
        """Return a deterministic vector derived from the SHA-256 of *text*.

        The 32-byte digest is cycled as needed to produce exactly
        :attr:`dimensions` float values in the range [0, 1).
        """
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: List[float] = []
        for i in range(self._dimensions):
            byte_val = digest[i % len(digest)]
            values.append(byte_val / 255.0)
        return values
