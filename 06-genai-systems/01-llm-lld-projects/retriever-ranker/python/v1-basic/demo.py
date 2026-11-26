"""
Retriever–Ranker demo — v1 basic.

Walks through the full pipeline:
    1. Index sample documents with embeddings and text
    2. Dense retrieval (cosine similarity)
    3. Sparse retrieval (TF-IDF keyword matching)
    4. Hybrid retrieval (alpha-blended)
    5. Ranking with different strategies
    6. Pipeline end-to-end query

Run:
    python demo.py
"""

from ranker import (
    RetrievalPipeline,
    RoundRobinRanker,
    ScoreRanker,
    WeightedRanker,
)
from result import RetrievalResult
from retriever import DenseRetriever, HybridRetriever, SparseRetriever


# ---------------------------------------------------------------------------
# Sample data
# ---------------------------------------------------------------------------

DOCUMENTS = [
    {
        "id": "chunk-1",
        "text": "Retrieval-Augmented Generation combines a retrieval step with a generative model.",
        "embedding": [0.9, 0.1, 0.2, 0.0],
        "meta": {"source": "rag-overview.md", "topic": "rag"},
    },
    {
        "id": "chunk-2",
        "text": "Dense retrieval uses vector embeddings to find semantically similar passages.",
        "embedding": [0.8, 0.3, 0.1, 0.1],
        "meta": {"source": "retrieval.md", "topic": "dense"},
    },
    {
        "id": "chunk-3",
        "text": "Sparse retrieval relies on keyword matching and term frequency for scoring.",
        "embedding": [0.1, 0.8, 0.3, 0.0],
        "meta": {"source": "retrieval.md", "topic": "sparse"},
    },
    {
        "id": "chunk-4",
        "text": "Hybrid search blends dense and sparse signals for better recall and precision.",
        "embedding": [0.5, 0.5, 0.4, 0.2],
        "meta": {"source": "hybrid.md", "topic": "hybrid"},
    },
    {
        "id": "chunk-5",
        "text": "Ranking algorithms order retrieved results by relevance before presenting them.",
        "embedding": [0.2, 0.1, 0.9, 0.3],
        "meta": {"source": "ranking.md", "topic": "ranking"},
    },
]


def main() -> None:
    print("=" * 60)
    print("RETRIEVER–RANKER DEMO (v1-basic)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Index documents
    # ------------------------------------------------------------------
    print("\n--- Indexing Documents ---")
    dense = DenseRetriever()
    sparse = SparseRetriever()

    for doc in DOCUMENTS:
        dense.add_document(doc["id"], doc["text"], doc["embedding"], doc["meta"])
        sparse.add_document(doc["id"], doc["text"], doc["meta"])
    print(f"  Indexed {dense.size} documents in dense retriever")
    print(f"  Indexed {sparse.size} documents in sparse retriever")

    # ------------------------------------------------------------------
    # 2. Dense retrieval
    # ------------------------------------------------------------------
    print("\n--- Dense Retrieval (query ≈ RAG embedding) ---")
    query_embedding = [0.85, 0.15, 0.2, 0.05]
    dense_results = dense.retrieve(query_embedding, top_k=3)
    for r in dense_results:
        print(f"  score={r.score:.4f}  [{r.chunk_id}] {r.content[:50]}...")

    # ------------------------------------------------------------------
    # 3. Sparse retrieval
    # ------------------------------------------------------------------
    print("\n--- Sparse Retrieval (query = 'dense vector retrieval') ---")
    query_text = "dense vector retrieval"
    sparse_results = sparse.retrieve(query_text, top_k=3)
    for r in sparse_results:
        print(f"  score={r.score:.4f}  [{r.chunk_id}] {r.content[:50]}...")

    # ------------------------------------------------------------------
    # 4. Hybrid retrieval
    # ------------------------------------------------------------------
    print("\n--- Hybrid Retrieval (alpha=0.6) ---")
    hybrid = HybridRetriever(dense, sparse, alpha=0.6)
    hybrid_results = hybrid.retrieve((query_embedding, query_text), top_k=3)
    for r in hybrid_results:
        print(f"  score={r.score:.4f}  [{r.chunk_id}] {r.content[:50]}...")

    # ------------------------------------------------------------------
    # 5. Score ranking
    # ------------------------------------------------------------------
    print("\n--- Score Ranking ---")
    score_ranker = ScoreRanker()
    all_results = dense_results + sparse_results
    ranked = score_ranker.rank(all_results, top_k=3)
    print(f"  Total candidates: {ranked.total_candidates}")
    for r in ranked:
        print(f"  score={r.score:.4f}  [{r.source}] {r.content[:50]}...")

    # ------------------------------------------------------------------
    # 6. Weighted ranking
    # ------------------------------------------------------------------
    print("\n--- Weighted Ranking (dense=1.5, sparse=0.8) ---")
    weighted_ranker = WeightedRanker(
        weights={"dense": 1.5, "sparse": 0.8}
    )
    ranked = weighted_ranker.rank(all_results, top_k=3)
    for r in ranked:
        print(f"  score={r.score:.4f}  [{r.source}] {r.content[:50]}...")

    # ------------------------------------------------------------------
    # 7. Round-robin ranking
    # ------------------------------------------------------------------
    print("\n--- Round-Robin Ranking ---")
    rr_ranker = RoundRobinRanker()
    ranked = rr_ranker.rank(all_results, top_k=4)
    for r in ranked:
        print(f"  score={r.score:.4f}  [{r.source}] {r.content[:50]}...")

    # ------------------------------------------------------------------
    # 8. Pipeline end-to-end
    # ------------------------------------------------------------------
    print("\n--- Pipeline (Dense + ScoreRanker) ---")
    pipeline = RetrievalPipeline(dense, ScoreRanker())
    result_set = pipeline.query(query_embedding, top_k=3)
    print(f"  Total candidates: {result_set.total_candidates}")
    for r in result_set:
        print(f"  score={r.score:.4f}  [{r.chunk_id}] {r.content[:50]}...")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
