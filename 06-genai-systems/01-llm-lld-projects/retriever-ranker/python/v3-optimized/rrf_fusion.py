from typing import Any, Dict, List
from collections import defaultdict

from result import RankedResultSet, RetrievalResult
from ranker import Ranker

class RRFFusionRanker(Ranker):
    """Rank results using Reciprocal Rank Fusion (RRF) with normalization.

    RRF combines results from multiple sources.
    Score formula: RRF_score = sum(1 / (k + rank_in_source))

    The scores are then normalized to [0.0, 1.0].
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

        # Compute raw RRF scores
        rrf_scores: Dict[str, float] = defaultdict(float)
        best_results: Dict[str, RetrievalResult] = {}

        for source, source_list in source_results.items():
            for rank, r in enumerate(source_list, start=1):
                rrf_scores[r.chunk_id] += 1.0 / (self.k + rank)
                if r.chunk_id not in best_results:
                    best_results[r.chunk_id] = r

        # Normalize RRF scores to [0.0, 1.0]
        if rrf_scores:
            max_score = max(rrf_scores.values())
        else:
            max_score = 1.0

        if max_score == 0:
            max_score = 1.0 # prevent division by zero

        # Create new results with normalized RRF scores
        merged_results: List[RetrievalResult] = []
        for chunk_id, score in rrf_scores.items():
            orig = best_results[chunk_id]
            normalized_score = score / max_score
            merged_results.append(RetrievalResult(
                chunk_id=chunk_id,
                content=orig.content,
                score=normalized_score,
                metadata=dict(orig.metadata),
                source="rrf",
            ))

        # Sort by RRF score
        merged_results.sort(key=lambda r: r.score, reverse=True)

        return RankedResultSet(
            results=merged_results[:top_k],
            total_candidates=len(results),
        )
