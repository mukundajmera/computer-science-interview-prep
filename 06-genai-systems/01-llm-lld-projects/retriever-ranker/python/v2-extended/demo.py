"""
Demo for v2-extended Retriever-Ranker pipeline.

Demonstrates:
    - RRF Ranker
    - Dynamic Alpha Retriever
    - Cross-Encoder Mock Ranker
"""

from result import RetrievalResult
from retriever import DenseRetriever, SparseRetriever
from dynamic_alpha import DynamicHybridRetriever
from ranker import RetrievalPipeline, ScoreRanker
from rrf_ranker import RRFRanker
from cross_encoder_mock import CrossEncoderMockRanker


def main() -> None:
    print("--- v2-extended Demo ---")

    # 1. Setup Data
    dense = DenseRetriever()
    sparse = SparseRetriever()

    corpus = [
        ("c1", "The quick brown fox jumps over the lazy dog.", [1.0, 0.0, 0.0]),
        ("c2", "Fast brown foxes leap across sleepy hounds.", [0.9, 0.1, 0.0]),
        ("c3", "A slow red fox walks around the active cat.", [0.1, 0.9, 0.0]),
        ("c4", "Dogs and cats are common household pets.", [0.0, 0.0, 1.0]),
    ]

    for chunk_id, content, embedding in corpus:
        dense.add_document(chunk_id, content, embedding)
        sparse.add_document(chunk_id, content)

    # 2. Dynamic Hybrid Retriever + RRF Ranker
    print("\n--- Dynamic Alpha + RRF Ranker ---")
    dynamic_hybrid = DynamicHybridRetriever(dense, sparse)
    rrf_ranker = RRFRanker(k=60)
    pipeline_rrf = RetrievalPipeline(dynamic_hybrid, rrf_ranker)

    query_embedding = [0.8, 0.2, 0.0]
    query_text = "quick brown fox?"

    # The DynamicHybridRetriever will compute alpha based on query_text
    print(f"Query: '{query_text}'")
    result_set_rrf = pipeline_rrf.query((query_embedding, query_text), top_k=3)

    for r in result_set_rrf.results:
        print(f"  [{r.chunk_id}] (score={r.score:.4f}, source={r.source}): {r.content}")

    # 3. Dynamic Hybrid Retriever + Cross Encoder Ranker
    print("\n--- Dynamic Alpha + Cross-Encoder Ranker ---")
    cross_encoder = CrossEncoderMockRanker()
    pipeline_ce = RetrievalPipeline(dynamic_hybrid, cross_encoder)

    query_text_2 = "fox jumps over"
    print(f"Query: '{query_text_2}'")
    result_set_ce = pipeline_ce.query((query_embedding, query_text_2), top_k=3)

    for r in result_set_ce.results:
        print(f"  [{r.chunk_id}] (score={r.score:.4f}, source={r.source}): {r.content}")


if __name__ == "__main__":
    main()
