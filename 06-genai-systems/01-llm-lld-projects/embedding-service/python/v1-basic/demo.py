"""
Embedding Service demo — v1 basic.

Walks through the full service:
    1. Create a model and cache
    2. Embed a single text
    3. Embed the same text again (cache hit)
    4. Batch-embed multiple texts
    5. Display stats and metrics

Run:
    python demo.py
"""

from embedding_model import HashEmbeddingModel, RandomEmbeddingModel
from cache import EmbeddingCache
from service import EmbeddingService


def main() -> None:
    print("=" * 60)
    print("EMBEDDING SERVICE DEMO (v1-basic)")
    print("=" * 60)

    # ------------------------------------------------------------------
    # 1. Setup: deterministic hash model + cache
    # ------------------------------------------------------------------
    model = HashEmbeddingModel(dimensions=8)
    cache = EmbeddingCache(max_size=100, ttl_seconds=60)
    service = EmbeddingService(model=model, cache=cache)

    print(f"\nModel: {model.model_name}  Dimensions: {model.dimensions}")
    print(f"Cache max_size: 100  TTL: 60s")

    # ------------------------------------------------------------------
    # 2. Single embedding
    # ------------------------------------------------------------------
    print("\n--- Single Embedding ---")
    result = service.embed("How does RAG work?")
    print(f"  Text:    {result.text}")
    print(f"  Vector:  [{', '.join(f'{v:.4f}' for v in result.embedding[:4])}...]")
    print(f"  Cached:  {result.cached}")
    print(f"  Dims:    {result.dimensions}")

    # ------------------------------------------------------------------
    # 3. Cache hit
    # ------------------------------------------------------------------
    print("\n--- Cache Hit (same text) ---")
    result2 = service.embed("How does RAG work?")
    print(f"  Cached:  {result2.cached}")
    print(f"  Vectors match: {result.embedding == result2.embedding}")

    # ------------------------------------------------------------------
    # 4. Batch embedding
    # ------------------------------------------------------------------
    print("\n--- Batch Embedding ---")
    texts = [
        "Vector databases store embeddings.",
        "Chunking splits documents into pieces.",
        "Cosine similarity measures vector closeness.",
    ]
    results = service.embed_batch(texts)
    for r in results:
        print(f"  [{r.cached}] {r.text[:45]}... → dim={r.dimensions}")

    # ------------------------------------------------------------------
    # 5. Stats
    # ------------------------------------------------------------------
    print("\n--- Service Stats ---")
    stats = service.get_stats()
    print(f"  Model:            {stats['model']}")
    print(f"  Dimensions:       {stats['dimensions']}")
    print(f"  Total embeddings: {stats['total_embeddings']}")
    if "cache" in stats:
        c = stats["cache"]
        print(f"  Cache hits:       {c['hits']}")
        print(f"  Cache misses:     {c['misses']}")
        print(f"  Cache hit rate:   {c['hit_rate']:.2%}")
        print(f"  Cache size:       {c['size']}")

    # ------------------------------------------------------------------
    # 6. Random model demo
    # ------------------------------------------------------------------
    print("\n--- Random Model (non-deterministic) ---")
    rand_model = RandomEmbeddingModel(dimensions=4)
    rand_service = EmbeddingService(model=rand_model)
    r1 = rand_service.embed("test")
    r2 = rand_service.embed("test")
    print(f"  Embed 1: [{', '.join(f'{v:.4f}' for v in r1.embedding)}]")
    print(f"  Embed 2: [{', '.join(f'{v:.4f}' for v in r2.embedding)}]")
    print(f"  Same?    {r1.embedding == r2.embedding}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
