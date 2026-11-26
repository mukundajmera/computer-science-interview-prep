"""
Index backend module.

Provides an abstract :class:`IndexBackend` interface and a brute-force
:class:`InMemoryIndex` implementation that uses cosine similarity for
nearest-neighbor search.

Design patterns:
    - Factory — callers can instantiate backends by name
    - Strategy — swap backend without changing pipeline code
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List

from chunker import Chunk


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class IndexEntry:
    """A single record in the index: a chunk paired with its embedding.

    Attributes:
        chunk:     The indexed :class:`Chunk`.
        embedding: Dense vector representation (``List[float]``).
        score:     Similarity score, populated during search (default 0.0).
    """

    chunk: Chunk
    embedding: List[float]
    score: float = 0.0


# ---------------------------------------------------------------------------
# Abstract backend
# ---------------------------------------------------------------------------

class IndexBackend(ABC):
    """Abstract interface for chunk–embedding storage and retrieval.

    Concrete implementations may wrap in-memory structures, FAISS, Pinecone,
    Weaviate, or any other vector database.
    """

    @abstractmethod
    def add(self, chunk: Chunk, embedding: List[float]) -> None:
        """Insert or update a chunk–embedding pair.

        Args:
            chunk:     The chunk to index.
            embedding: Its dense vector representation.
        """

    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[IndexEntry]:
        """Return the *top_k* most similar entries to *query_embedding*.

        Args:
            query_embedding: The query vector.
            top_k:           Maximum number of results.

        Returns:
            A list of :class:`IndexEntry` sorted by descending similarity.
        """

    @abstractmethod
    def delete(self, chunk_id: str) -> bool:
        """Remove the entry identified by *chunk_id*.

        Returns:
            ``True`` if an entry was removed, ``False`` if not found.
        """

    @abstractmethod
    def size(self) -> int:
        """Return the number of entries currently stored."""


# ---------------------------------------------------------------------------
# In-memory implementation
# ---------------------------------------------------------------------------

class InMemoryIndex(IndexBackend):
    """Brute-force in-memory vector index.

    Stores entries in a :class:`dict` keyed by ``chunk_id`` and performs
    linear-scan cosine-similarity search.

    Complexity:
        - add:    O(1)
        - search: O(k · d)  where k = stored entries, d = embedding dim
        - delete: O(1)
    """

    def __init__(self) -> None:
        self._entries: Dict[str, IndexEntry] = {}

    # -- public API --------------------------------------------------------

    def add(self, chunk: Chunk, embedding: List[float]) -> None:
        """Insert or overwrite a chunk–embedding pair."""
        if not embedding:
            raise ValueError("Embedding must not be empty")
        self._entries[chunk.chunk_id] = IndexEntry(chunk=chunk, embedding=embedding)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[IndexEntry]:
        """Brute-force cosine-similarity search.

        Returns up to *top_k* entries sorted by descending similarity.
        """
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if not query_embedding:
            raise ValueError("Query embedding must not be empty")

        scored: List[IndexEntry] = []
        for entry in self._entries.values():
            sim = self._cosine_similarity(query_embedding, entry.embedding)
            scored.append(IndexEntry(
                chunk=entry.chunk,
                embedding=entry.embedding,
                score=sim,
            ))

        scored.sort(key=lambda e: e.score, reverse=True)
        return scored[:top_k]

    def delete(self, chunk_id: str) -> bool:
        """Remove entry by *chunk_id*. Returns ``True`` on success."""
        if chunk_id in self._entries:
            del self._entries[chunk_id]
            return True
        return False

    def size(self) -> int:
        """Return number of stored entries."""
        return len(self._entries)

    # -- private helpers ---------------------------------------------------

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors.

        Returns 0.0 when either vector has zero magnitude.

        Complexity: O(d) where d = len(a).
        """
        if len(a) != len(b):
            raise ValueError(
                f"Dimension mismatch: {len(a)} vs {len(b)}"
            )
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)
