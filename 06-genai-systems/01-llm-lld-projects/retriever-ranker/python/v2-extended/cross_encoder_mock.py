from typing import Any, List
from result import RankedResultSet, RetrievalResult
from ranker import Ranker

class CrossEncoderMockRanker(Ranker):
    """Mocks a heavy cross-encoder LLM model for re-ranking.

    Instead of actually calling an LLM, this mock ranker recalculates
    relevance scores based on simple textual overlap/heuristics between
    the query and document text.
    """

    def rank(
        self,
        results: List[RetrievalResult],
        top_k: int = 10,
        query: Any = None,
    ) -> RankedResultSet:
        self._validate_top_k(top_k)

        # We need the query text to perform "cross-encoder" scoring.
        # Assuming query could be a tuple (embedding, text) or just text.
        query_text = ""
        if isinstance(query, tuple) and len(query) == 2:
            query_text = query[1]
        elif isinstance(query, str):
            query_text = query

        if not query_text:
            # Fallback to original score if no query text available
            return RankedResultSet(results=results[:top_k], total_candidates=len(results))

        query_words = set(query_text.lower().split())

        rescored_results: List[RetrievalResult] = []
        for r in results:
            doc_words = set(r.content.lower().split())

            # Simple Jaccard similarity as mock cross-encoder score
            if not query_words or not doc_words:
                new_score = 0.0
            else:
                intersection = query_words.intersection(doc_words)
                union = query_words.union(doc_words)
                new_score = len(intersection) / len(union)

            rescored_results.append(RetrievalResult(
                chunk_id=r.chunk_id,
                content=r.content,
                score=new_score,
                metadata=dict(r.metadata),
                source="cross_encoder",
            ))

        # Sort by cross encoder score
        rescored_results.sort(key=lambda r: r.score, reverse=True)

        return RankedResultSet(
            results=rescored_results[:top_k],
            total_candidates=len(results),
        )
