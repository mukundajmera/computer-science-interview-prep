"""
Ranker module — V1 Basic.

Provides ranking strategies that order retrieval results and a pipeline
class that chains retrieval and ranking into a single entry point.

Design patterns:
    - Strategy        — interchangeable ranking algorithms
    - Template Method — common validation / truncation in the pipeline
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List

from result import RankedResultSet, RetrievalResult
from retriever import Retriever


# ---------------------------------------------------------------------------
# Ranker ABC
# ---------------------------------------------------------------------------

class Ranker(ABC):
    """Abstract base for ranking strategies.

    Subclasses implement :meth:`rank` which orders a list of retrieval
    results and returns a :class:`RankedResultSet`.
    """

    @abstractmethod
    def rank(
        self,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> RankedResultSet:
        """Order *results* and return the top-*k* as a :class:`RankedResultSet`.

        Args:
            results: Unordered retrieval results.
            top_k:   Maximum number of results to include.

        Returns:
            An ordered :class:`RankedResultSet`.
        """

    @staticmethod
    def _validate_top_k(top_k: int) -> None:
        """Raise ``ValueError`` if *top_k* is not positive."""
        if top_k <= 0:
            raise ValueError("top_k must be positive")


# ---------------------------------------------------------------------------
# Concrete rankers
# ---------------------------------------------------------------------------

class ScoreRanker(Ranker):
    """Rank results by descending score.

    The simplest ranking strategy — sorts results by their existing
    ``score`` attribute and truncates to top-k.

    Complexity: O(n log n) where n = number of results.
    """

    def rank(
        self,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> RankedResultSet:
        """Sort *results* by descending score and return top-*k*."""
        self._validate_top_k(top_k)
        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
        return RankedResultSet(
            results=sorted_results[:top_k],
            total_candidates=len(results),
        )


class RoundRobinRanker(Ranker):
    """Interleave results from multiple sources in round-robin order.

    Groups results by their ``source`` field, then picks one from each
    group in turn.  Within each group, results are ordered by descending
    score before interleaving.

    Complexity: O(n log n) for the initial sort, O(n) for interleaving.
    """

    def rank(
        self,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> RankedResultSet:
        """Interleave *results* by source and return top-*k*."""
        self._validate_top_k(top_k)

        # Group by source, sorted within each group
        groups: Dict[str, List[RetrievalResult]] = defaultdict(list)
        for r in results:
            groups[r.source].append(r)
        for source in groups:
            groups[source].sort(key=lambda r: r.score, reverse=True)

        # Round-robin interleave
        interleaved: List[RetrievalResult] = []
        source_keys = sorted(groups.keys())
        indices = {s: 0 for s in source_keys}
        exhausted = 0

        while exhausted < len(source_keys) and len(interleaved) < top_k:
            for source in source_keys:
                if indices[source] >= len(groups[source]):
                    continue
                interleaved.append(groups[source][indices[source]])
                indices[source] += 1
                if indices[source] >= len(groups[source]):
                    exhausted += 1
                if len(interleaved) >= top_k:
                    break

        return RankedResultSet(
            results=interleaved[:top_k],
            total_candidates=len(results),
        )


class WeightedRanker(Ranker):
    """Apply source-specific weights to scores before ranking.

    Each result's score is multiplied by the weight configured for its
    ``source``.  Results are then sorted by the weighted score.

    Args:
        weights:        Mapping of source name → weight multiplier.
        default_weight: Fallback weight for sources not in *weights*.

    Complexity: O(n log n) where n = number of results.
    """

    def __init__(
        self,
        weights: Dict[str, float] | None = None,
        default_weight: float = 1.0,
    ) -> None:
        self._weights: Dict[str, float] = dict(weights) if weights else {}
        self._default_weight = default_weight

    def rank(
        self,
        results: List[RetrievalResult],
        top_k: int = 10,
    ) -> RankedResultSet:
        """Apply weights, sort by weighted score, and return top-*k*.

        The original ``score`` on each result is **replaced** with the
        weighted score in the returned set.
        """
        self._validate_top_k(top_k)

        weighted: List[RetrievalResult] = []
        for r in results:
            w = self._weights.get(r.source, self._default_weight)
            weighted.append(RetrievalResult(
                chunk_id=r.chunk_id,
                content=r.content,
                score=r.score * w,
                metadata=dict(r.metadata),
                source=r.source,
            ))

        weighted.sort(key=lambda r: r.score, reverse=True)
        return RankedResultSet(
            results=weighted[:top_k],
            total_candidates=len(results),
        )


# ---------------------------------------------------------------------------
# Pipeline orchestrator
# ---------------------------------------------------------------------------

class RetrievalPipeline:
    """Chain a :class:`Retriever` and :class:`Ranker` into a single query.

    The pipeline is stateless — each query is independent.

    Args:
        retriever: Fetches candidate results.
        ranker:    Orders candidate results.
    """

    def __init__(self, retriever: Retriever, ranker: Ranker) -> None:
        self._retriever = retriever
        self._ranker = ranker

    @property
    def retriever(self) -> Retriever:
        """Return the current retriever."""
        return self._retriever

    @property
    def ranker(self) -> Ranker:
        """Return the current ranker."""
        return self._ranker

    def query(self, query: Any, top_k: int = 10) -> RankedResultSet:
        """Run the full retrieve → rank pipeline.

        Args:
            query: Query representation passed to the retriever.
            top_k: Maximum number of final ranked results.

        Returns:
            A :class:`RankedResultSet` with at most *top_k* results.
        """
        # Retrieve a larger candidate pool, then let the ranker select top-k
        fetch_k = top_k * 3
        candidates = self._retriever.retrieve(query, top_k=fetch_k)
        return self._ranker.rank(candidates, top_k=top_k)
