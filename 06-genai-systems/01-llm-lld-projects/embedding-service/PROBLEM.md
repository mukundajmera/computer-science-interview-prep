# Embedding Service

## Problem Statement

Design an embedding service that accepts text strings and returns dense vector embeddings. The service should support pluggable embedding model backends, batch processing, in-memory caching with configurable TTL to avoid recomputation, L2 normalization of output vectors, and basic operational metrics. The system should be extensible enough that new embedding models can be added without modifying existing code.

---

## Functional Requirements

1. **Single Text Embedding**: Accept a text string and return a dense vector embedding
2. **Batch Embedding**: Accept multiple texts and return embeddings for all in one call
3. **Pluggable Model Backends**: Support swappable embedding model implementations via a common interface
4. **Embedding Caching**: Cache computed embeddings in memory with configurable TTL and max size to avoid redundant computation
5. **L2 Normalization**: Normalize all output embeddings to unit length (L2 norm = 1.0)
6. **Input Validation**: Reject empty strings, whitespace-only inputs, and detect dimension mismatches
7. **Operational Metrics**: Report cache hit rate, total embedding count, and model information

---

## Non-Functional Requirements

1. **Extensibility**: Adding a new embedding model must not require changes to existing classes (Open/Closed Principle)
2. **Testability**: Every component must be independently unit-testable with deterministic stub models
3. **Performance**: Caching should provide O(1) lookup; batch processing should be more efficient than sequential single calls
4. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively
5. **Determinism**: At least one model backend must produce deterministic outputs for repeatable testing

---

## Constraints & Assumptions

- Embeddings are represented as `List[float]` — the service uses stub models (no real neural network inference)
- `RandomEmbeddingModel` generates random vectors for demonstration purposes
- `HashEmbeddingModel` generates deterministic vectors from text hashes for testing
- Cache keys are derived from text content and model name
- TTL-based expiry uses `time.time()` for simplicity
- Cache eviction removes the oldest entry when capacity is exceeded
- All embeddings from a given model have the same dimensionality

---

## Sample Interactions

```
1. Caller creates an EmbeddingModel (e.g., HashEmbeddingModel(dimensions=128))
2. Caller creates an EmbeddingCache (e.g., EmbeddingCache(max_size=1000, ttl_seconds=300))
3. Caller creates an EmbeddingService(model=model, cache=cache)
4. service.embed("How does RAG work?") → EmbeddingResult(text=..., embedding=[...], cached=False)
5. service.embed("How does RAG work?") → EmbeddingResult(text=..., embedding=[...], cached=True)
6. service.embed_batch(["text1", "text2", "text3"]) → [EmbeddingResult, ...]
7. service.get_stats() → {"model": "hash", "dimensions": 128, "total_embeddings": 4, ...}
```

---

## Clarifying Questions to Ask

1. "What embedding dimensionality should the service produce?"
2. "Should the cache persist across service restarts, or is in-memory sufficient?"
3. "What is the expected average text length for embedding?"
4. "Should batch embedding be parallelized, or is sequential processing acceptable?"
5. "Do we need to support multiple models simultaneously, or one model per service instance?"
6. "What should the TTL be for cached embeddings?"
7. "Should the service normalize embeddings by default, or make it optional?"
8. "How should very long texts be handled — truncation or error?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| EmbeddingRequest | Input data carrier: text and optional model name |
| EmbeddingResult | Output data carrier: text, embedding vector, metadata, cached flag |
| EmbeddingModel | Abstract interface for embedding generation backends |
| RandomEmbeddingModel | Stub model producing random embeddings (for demos) |
| HashEmbeddingModel | Stub model producing deterministic hash-based embeddings (for testing) |
| EmbeddingCache | In-memory cache with TTL and max-size eviction |
| EmbeddingService | Orchestrator combining model, cache, normalization, and validation |

---

## Cross-References

- [Vector Databases concept](../../00-concepts/vector-databases/) — embedding storage and similarity search
- [RAG Architecture concept](../../00-concepts/rag-architecture/) — how embeddings fit in the retrieval pipeline
- [Document QA RAG (HLD)](../../02-llm-hld-projects/document-qa-rag/) — system design that consumes embeddings
- [Caching (classical HLD concept)](../../../03-hld-concepts/caching/) — general caching strategies and eviction policies

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Pluggable models (random, hash stubs), in-memory cache with TTL/eviction, L2 normalization, batch embedding, input validation, metrics |
| v2-extended | Embedding truncation/padding, model warm-up, async batch processing, cache persistence (JSON), similarity comparison utility |
| v3-optimized | Connection pool for remote model backends, LRU eviction, cache sharding, streaming batch embeddings, embedding quantization stubs |
