"""
Retriever module — V1 Basic.

Provides a Strategy-based framework for retrieving documents from an
in-memory index.  Three built-in strategies are included: dense (cosine
similarity), sparse (TF-IDF), and hybrid (alpha-blended composite).

Design patterns:
    - Strategy        — interchangeable retrieval algorithms
    - Composite       — HybridRetriever composes dense + sparse
    - Template Method — shared validation / truncation in the ABC
"""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any, Dict, List

from result import RetrievalResult


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------

class Retriever(ABC):
    """Abstract base for retrieval strategies.

    Subclasses implement :meth:`_fetch` which returns **all** matching
    results.  The public :meth:`retrieve` method handles validation and
    top-k truncation.
    """

    def retrieve(self, query: Any, top_k: int = 10) -> List[RetrievalResult]:
        """Retrieve the top-*k* results for *query*.

        Args:
            query: Query representation (embedding vector, text, or tuple).
            top_k: Maximum number of results to return.

        Raises:
            ValueError: If *top_k* is not positive.
        """
        self._validate_top_k(top_k)
        results = self._fetch(query)
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    @abstractmethod
    def _fetch(self, query: Any) -> List[RetrievalResult]:
        """Return all candidate results for *query* (unsorted)."""

    @staticmethod
    def _validate_top_k(top_k: int) -> None:
        """Raise ``ValueError`` if *top_k* is not positive."""
        if top_k <= 0:
            raise ValueError("top_k must be positive")


# ---------------------------------------------------------------------------
# Dense retriever (cosine similarity)
# ---------------------------------------------------------------------------

class DenseRetriever(Retriever):
    """Retrieve documents by cosine similarity over in-memory vectors.

    Documents must be added via :meth:`add_document` before querying.

    Complexity: O(n · d) per query, where *n* = documents, *d* = dimension.
    """

    def __init__(self) -> None:
        self._vectors: Dict[str, List[float]] = {}
        self._documents: Dict[str, str] = {}
        self._metadata: Dict[str, Dict[str, str]] = {}

    def add_document(
        self,
        chunk_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, str] | None = None,
    ) -> None:
        """Index a document with its embedding vector.

        Args:
            chunk_id:  Unique identifier for the chunk.
            content:   Text content of the chunk.
            embedding: Dense vector representation.
            metadata:  Optional key-value annotations.

        Raises:
            ValueError: If *embedding* is empty.
        """
        if not embedding:
            raise ValueError("embedding must not be empty")
        self._vectors[chunk_id] = embedding
        self._documents[chunk_id] = content
        self._metadata[chunk_id] = metadata or {}

    @property
    def size(self) -> int:
        """Return the number of indexed documents."""
        return len(self._vectors)

    def _fetch(self, query: Any) -> List[RetrievalResult]:
        """Compute cosine similarity between *query* and all stored vectors."""
        query_embedding: List[float] = query
        if not query_embedding:
            raise ValueError("query embedding must not be empty")

        results: List[RetrievalResult] = []
        for chunk_id, vec in self._vectors.items():
            if len(vec) != len(query_embedding):
                raise ValueError(
                    f"Dimension mismatch: query={len(query_embedding)}, "
                    f"document={len(vec)}"
                )
            score = self._cosine_similarity(query_embedding, vec)
            results.append(RetrievalResult(
                chunk_id=chunk_id,
                content=self._documents[chunk_id],
                score=score,
                metadata=dict(self._metadata[chunk_id]),
                source="dense",
            ))
        return results

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors.

        Returns 0.0 if either vector has zero magnitude.
        """
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# Sparse retriever (TF-IDF)
# ---------------------------------------------------------------------------

class SparseRetriever(Retriever):
    """Retrieve documents using BM25 keyword matching (TF-IDF weighted).

    Uses simple whitespace tokenization and BM25 term frequency saturation
    with inverse-document-frequency scoring. IDF is recomputed on each document add.

    Complexity: O(n · q) per query, where *n* = documents, *q* = query terms.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._corpus: Dict[str, str] = {}
        self._metadata: Dict[str, Dict[str, str]] = {}
        self._idf: Dict[str, float] = {}
        self._tf: Dict[str, Dict[str, int]] = {}
        self._doc_len: Dict[str, int] = {}
        self._avgdl: float = 0.0

    def add_document(
        self,
        chunk_id: str,
        content: str,
        metadata: Dict[str, str] | None = None,
    ) -> None:
        """Index a document for keyword retrieval.

        Args:
            chunk_id: Unique identifier for the chunk.
            content:  Text content of the chunk.
            metadata: Optional key-value annotations.
        """
        self._corpus[chunk_id] = content
        self._metadata[chunk_id] = metadata or {}
        tokens = self._tokenize(content)
        self._doc_len[chunk_id] = len(tokens)
        self._compute_tf(chunk_id, tokens)
        self._compute_idf()
        
        # Recompute average document length
        total_len = sum(self._doc_len.values())
        self._avgdl = total_len / len(self._doc_len) if self._doc_len else 0.0

    @property
    def size(self) -> int:
        """Return the number of indexed documents."""
        return len(self._corpus)

    def _fetch(self, query: Any) -> List[RetrievalResult]:
        """Score all documents against *query* using BM25."""
        query_text: str = query
        if not query_text or not query_text.strip():
            return []

        query_tokens = self._tokenize(query_text)
        if not query_tokens:
            return []

        results: List[RetrievalResult] = []
        for chunk_id, tf_map in self._tf.items():
            score = 0.0
            dl = self._doc_len.get(chunk_id, 0)
            if dl > 0 and self._avgdl > 0:
                for token in query_tokens:
                    tf_val = tf_map.get(token, 0)
                    if tf_val > 0:
                        idf_val = self._idf.get(token, 0.0)
                        
                        # BM25 tf saturation
                        numerator = tf_val * (self.k1 + 1)
                        denominator = tf_val + self.k1 * (1 - self.b + self.b * (dl / self._avgdl))
                        
                        score += idf_val * (numerator / denominator)
                        
            results.append(RetrievalResult(
                chunk_id=chunk_id,
                content=self._corpus[chunk_id],
                score=score,
                metadata=dict(self._metadata[chunk_id]),
                source="sparse",
            ))
        return results

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Lowercase whitespace tokenization, stripping punctuation.

        Returns a list of non-empty lowercase tokens.
        """
        cleaned = ""
        for ch in text.lower():
            if ch.isalnum() or ch.isspace():
                cleaned += ch
            else:
                cleaned += " "
        return [t for t in cleaned.split() if t]

    def _compute_idf(self) -> None:
        """Recompute inverse document frequency for all terms.

        IDF(t) = log(N / df(t)) where *N* = total docs, *df(t)* = docs containing *t*.
        """
        n = len(self._corpus)
        if n == 0:
            self._idf = {}
            return

        df: Dict[str, int] = defaultdict(int)
        for tf_map in self._tf.values():
            for term in tf_map:
                df[term] += 1

        self._idf = {
            term: math.log(n / count) if count > 0 else 0.0
            for term, count in df.items()
        }

    def _compute_tf(self, chunk_id: str, tokens: List[str]) -> None:
        """Compute term frequencies for a document."""
        if not tokens:
            self._tf[chunk_id] = {}
            return

        counts: Dict[str, int] = defaultdict(int)
        for token in tokens:
            counts[token] += 1

        self._tf[chunk_id] = counts


# ---------------------------------------------------------------------------
# Hybrid retriever (composite)
# ---------------------------------------------------------------------------

class HybridRetriever(Retriever):
    """Combine dense and sparse retrieval with configurable alpha blending.

    Score formula: ``hybrid_score = alpha * dense_score + (1 - alpha) * sparse_score``

    When alpha = 1.0, only dense scores contribute.
    When alpha = 0.0, only sparse scores contribute.

    Design patterns:
        - Composite — composes two Retrievers behind the same interface

    Args:
        dense_retriever:  Dense retrieval source.
        sparse_retriever: Sparse retrieval source.
        alpha:            Blending weight in [0.0, 1.0].

    Raises:
        ValueError: If *alpha* is outside [0.0, 1.0].
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

    def retrieve(self, query: Any, top_k: int = 10) -> List[RetrievalResult]:
        """Retrieve from both sources, merge, and return top-*k* results.

        Args:
            query: A tuple of ``(query_embedding, query_text)`` for hybrid,
                   or a value compatible with the underlying retrievers.
            top_k: Maximum number of results to return.

        Raises:
            ValueError: If *top_k* is not positive or *query* is not a
                        ``(embedding, text)`` tuple.
        """
        self._validate_top_k(top_k)

        if isinstance(query, tuple) and len(query) == 2:
            query_embedding, query_text = query
        else:
            raise ValueError(
                "HybridRetriever query must be a (embedding, text) tuple"
            )

        # Retrieve a larger candidate pool from each source
        fetch_k = top_k * 3
        dense_results = self._dense.retrieve(query_embedding, top_k=fetch_k)
        sparse_results = self._sparse.retrieve(query_text, top_k=fetch_k)

        merged = self._merge_results(dense_results, sparse_results)
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged[:top_k]

    def _fetch(self, query: Any) -> List[RetrievalResult]:
        """Not used directly — :meth:`retrieve` overrides the full flow."""
        return []

    def _merge_results(
        self,
        dense_results: List[RetrievalResult],
        sparse_results: List[RetrievalResult],
    ) -> List[RetrievalResult]:
        """Alpha-blend scores from dense and sparse results.

        If a chunk_id appears in both lists, its scores are blended.
        If it appears in only one list, the missing score is treated as 0.0.
        """
        dense_map: Dict[str, RetrievalResult] = {
            r.chunk_id: r for r in dense_results
        }
        sparse_map: Dict[str, RetrievalResult] = {
            r.chunk_id: r for r in sparse_results
        }

        all_ids = set(dense_map.keys()) | set(sparse_map.keys())
        merged: List[RetrievalResult] = []

        for chunk_id in all_ids:
            dense_score = dense_map[chunk_id].score if chunk_id in dense_map else 0.0
            sparse_score = sparse_map[chunk_id].score if chunk_id in sparse_map else 0.0
            blended = self._alpha * dense_score + (1 - self._alpha) * sparse_score

            # Use whichever result exists for content/metadata
            base = dense_map.get(chunk_id) or sparse_map[chunk_id]
            merged.append(RetrievalResult(
                chunk_id=chunk_id,
                content=base.content,
                score=blended,
                metadata=dict(base.metadata),
                source="hybrid",
            ))

        return merged
