import asyncio
from retriever import DenseRetriever, SparseRetriever
from async_pipeline import AsyncHybridRetriever, AsyncRetrievalPipeline
from rrf_fusion import RRFFusionRanker

async def main():
    print("--- Retriever-Ranker v3 Optimized Demo ---")

    # 1. Setup indices
    dense = DenseRetriever()
    sparse = SparseRetriever()

    print("Indexing documents...")
    dense.add_document("doc1", "The quick brown fox jumps over the lazy dog", [1.0, 0.0, 0.0], {"source": "wiki"})
    sparse.add_document("doc1", "The quick brown fox jumps over the lazy dog", {"source": "wiki"})

    dense.add_document("doc2", "A fast brown fox", [0.8, 0.2, 0.0], {"source": "blog"})
    sparse.add_document("doc2", "A fast brown fox", {"source": "blog"})

    dense.add_document("doc3", "The lazy dog sleeps all day", [0.0, 0.0, 1.0], {"source": "wiki"})
    sparse.add_document("doc3", "The lazy dog sleeps all day", {"source": "wiki"})

    # 2. Setup async hybrid retriever and rrf ranker
    print("\nSetting up async pipeline with RRF Ranker...")
    async_hybrid = AsyncHybridRetriever(dense, sparse, alpha=0.5)
    rrf_ranker = RRFFusionRanker(k=60)
    pipeline = AsyncRetrievalPipeline(async_hybrid, rrf_ranker)

    # 3. Query
    query_text = "quick brown fox"
    query_vector = [1.0, 0.0, 0.0]
    query = (query_vector, query_text)

    print(f"\nQuerying: '{query_text}' (and vector)")
    ranked_results = await pipeline.query(query, top_k=2)

    print("\nResults:")
    for i, r in enumerate(ranked_results.results, 1):
        print(f"  {i}. [Score: {r.score:.4f}] {r.content} (Source: {r.source})")

if __name__ == "__main__":
    asyncio.run(main())
