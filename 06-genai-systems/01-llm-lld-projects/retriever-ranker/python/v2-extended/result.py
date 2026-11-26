"""
Retrieval result data types.

Provides the core data carriers used throughout the retriever–ranker
pipeline: individual retrieval hits and ordered result sets.

Design patterns:
    - Value Object — immutable-style data carriers with no business logic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RetrievalResult:
    """A single retrieval hit from a search query.

    Attributes:
        chunk_id: Unique identifier for the retrieved chunk.
        content:  Text content of the chunk.
        score:    Relevance score (0.0–1.0, higher is better).
        metadata: Key-value annotations (source document, tags, etc.).
        source:   Which retriever produced this result ("dense", "sparse", "hybrid").
    """

    chunk_id: str
    content: str
    score: float = 0.0
    metadata: Dict[str, str] = field(default_factory=dict)
    source: str = ""


class RankedResultSet:
    """An ordered collection of ranked retrieval results.

    Attributes:
        results:          Ordered list of results (best first).
        total_candidates: Total candidates considered before top-k truncation.
    """

    def __init__(
        self,
        results: List[RetrievalResult],
        total_candidates: int = 0,
    ) -> None:
        self.results = list(results)
        self.total_candidates = total_candidates if total_candidates else len(results)

    def top(self, k: int) -> "RankedResultSet":
        """Return a new :class:`RankedResultSet` with only the top-*k* results.

        Args:
            k: Maximum number of results to include.

        Returns:
            A new result set containing at most *k* results.

        Raises:
            ValueError: If *k* is not positive.
        """
        if k <= 0:
            raise ValueError("k must be positive")
        return RankedResultSet(
            results=self.results[:k],
            total_candidates=self.total_candidates,
        )

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self):
        return iter(self.results)

    def __repr__(self) -> str:
        return (
            f"RankedResultSet(count={len(self.results)}, "
            f"total_candidates={self.total_candidates})"
        )
