from typing import Any, Dict, List
from collections import defaultdict

from result import RankedResultSet, RetrievalResult
from ranker import Ranker

class RRFRanker(Ranker):
    """Rank results using Reciprocal Rank Fusion (RRF).

    RRF is useful when combining results from .multiple uncalibrated retrievers.
    Instead of relying on the raw score, it uses the rank of the document
    within each source's results.

    Score formula: RRF_score = sum(1 / (k + rank_in_source))
    """

    def __init__(self, k: int = 60) -> None:
        """Initialize RRF Ranker.

        Args:
            k: Smoothing constant for RRF. Default is 60.
        """
        self.k = k

    def rank(
        self,
        results: List[RetrievalResult],
        top_k: int = 10,
        query: Any = None,
    ) -> RankedResultSet:
        self._validate_top_k(top_k)

        # Group results by source
        source_results: Dict[str, List[RetrievalResult]] = defaultdict(list)
        for r in results:
            source_results[r.source].append(r)

        # Sort each source's results by raw score to determine ranks
        for source in source_results:
            source_results[source].sort(key=lambda r: r.score, reverse=True)

        # Compute RRF scores
        rrf_scores: Dict[str, float] = defaultdict(float)
        # We need to map chunk_id back to the first seen result item to keep content/metadata
        best_results: Dict[str, RetrievalResult] = {}

        for source, source_list in source_results.items():
            for rank, r in enumerate(source_list, start=1):
                rrf_scores[r.chunk_id] += 1.0 / (self.k + rank)
                if r.chunk_id not in best_results:
                    best_results[r.chunk_id] = r

        # Create new results with RRF scores
        merged_results: List[RetrievalResult] = []
        for chunk_id, score in rrf_scores.items():
            orig = best_results[chunk_id]
            merged_results.append(RetrievalResult(
                chunk_id=chunk_id,
                content=orig.content,
                score=score,
                metadata=dict(orig.metadata),
                source="rrf",
            ))

        # Sort by RRF score
        merged_results.sort(key=lambda r: r.score, reverse=True)

        return RankedResultSet(
            results=merged_results[:top_k],
            total_candidates=len(results),
        )
