from typing import Any, List, Tuple
from retriever import Retriever, HybridRetriever
from result import RetrievalResult

def compute_dynamic_alpha(query_text: str) -> float:
    """Compute dynamic alpha based on query characteristics.

    If the query is a full conversational question (e.g., contains '?',
    or has many words), we lean towards dense retrieval (alpha closer to 1.0).
    If it's mostly keywords (short, no punctuation), we lean towards
    sparse retrieval (alpha closer to 0.0).

    Returns:
        alpha value in [0.0, 1.0]
    """
    if not query_text:
        return 0.5

    words = query_text.split()
    num_words = len(words)

    is_question = "?" in query_text

    # Base alpha
    alpha = 0.5

    if is_question:
        alpha += 0.2

    if num_words > 5:
        alpha += 0.2
    elif num_words <= 2:
        alpha -= 0.3

    # Clamp between 0.0 and 1.0
    return max(0.0, min(1.0, alpha))


class DynamicHybridRetriever(HybridRetriever):
    """Hybrid Retriever that dynamically adjusts alpha based on the query."""

    def retrieve(self, query: Any, top_k: int = 10) -> List[RetrievalResult]:
        """Retrieve using a dynamically computed alpha.

        Args:
            query: A tuple of (query_embedding, query_text).
            top_k: Maximum number of results.
        """
        self._validate_top_k(top_k)

        if isinstance(query, tuple) and len(query) == 2:
            query_embedding, query_text = query
        else:
            raise ValueError(
                "DynamicHybridRetriever query must be a (embedding, text) tuple"
            )

        # Dynamically compute alpha
        self._alpha = compute_dynamic_alpha(query_text)

        # Retrieve
        fetch_k = top_k * 3
        dense_results = self._dense.retrieve(query_embedding, top_k=fetch_k)
        sparse_results = self._sparse.retrieve(query_text, top_k=fetch_k)

        merged = self._merge_results(dense_results, sparse_results)
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged[:top_k]
