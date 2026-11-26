import asyncio
from typing import Any, List

from retriever import Retriever
from ranker import Ranker
from result import RetrievalResult, RankedResultSet

class AsyncHybridRetriever:
    """Async multi-source hybrid retriever.

    Runs dense and sparse retrieval in parallel.
    """

    def __init__(
        self,
        dense_retriever: Retriever,
        sparse_retriever: Retriever,
        alpha: float = 0.5,
    ) -> None:
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("alpha must be between 0.0 and 1.0")
        self._dense = dense_retriever
        self._sparse = sparse_retriever
        self._alpha = alpha

    @property
    def alpha(self) -> float:
        """Return the current alpha blending weight."""
        return self._alpha

    def _validate_top_k(self, top_k: int) -> None:
        if top_k <= 0:
            raise ValueError("top_k must be positive")

    def _merge_results(
        self, dense_results: List[RetrievalResult], sparse_results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """Merge dense and sparse results using alpha-blended score."""
        combined = {}

        for r in dense_results:
            combined[r.chunk_id] = {
                "chunk_id": r.chunk_id,
                "content": r.content,
                "dense_score": r.score,
                "sparse_score": 0.0,
                "metadata": dict(r.metadata),
            }

        for r in sparse_results:
            if r.chunk_id in combined:
                combined[r.chunk_id]["sparse_score"] = r.score
            else:
                combined[r.chunk_id] = {
                    "chunk_id": r.chunk_id,
                    "content": r.content,
                    "dense_score": 0.0,
                    "sparse_score": r.score,
                    "metadata": dict(r.metadata),
                }

        merged = []
        for chunk_id, data in combined.items():
            final_score = self._alpha * data["dense_score"] + (1 - self._alpha) * data["sparse_score"]
            merged.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    content=data["content"],
                    score=final_score,
                    metadata=data["metadata"],
                    source="hybrid",
                )
            )

        return merged

    async def retrieve(self, query: Any, top_k: int = 10) -> List[RetrievalResult]:
        """Retrieve from both sources concurrently, merge, and return top-*k* results."""
        self._validate_top_k(top_k)

        if isinstance(query, tuple) and len(query) == 2:
            query_embedding, query_text = query
        else:
            raise ValueError("HybridRetriever query must be a (embedding, text) tuple")

        fetch_k = top_k * 3

        # Run retrievals concurrently
        loop = asyncio.get_running_loop()
        dense_task = loop.run_in_executor(None, self._dense.retrieve, query_embedding, fetch_k)
        sparse_task = loop.run_in_executor(None, self._sparse.retrieve, query_text, fetch_k)

        dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)

        merged = self._merge_results(dense_results, sparse_results)
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged[:top_k]


class AsyncRetrievalPipeline:
    """Async pipeline chaining an async retriever and a synchronous ranker."""

    def __init__(self, retriever: AsyncHybridRetriever, ranker: Ranker) -> None:
        self._retriever = retriever
        self._ranker = ranker

    @property
    def retriever(self) -> AsyncHybridRetriever:
        return self._retriever

    @property
    def ranker(self) -> Ranker:
        return self._ranker

    async def query(self, query: Any, top_k: int = 10) -> RankedResultSet:
        """Run the full async retrieve -> rank pipeline."""
        results = await self._retriever.retrieve(query, top_k=top_k * 3)
        return self._ranker.rank(results, top_k=top_k, query=query)
