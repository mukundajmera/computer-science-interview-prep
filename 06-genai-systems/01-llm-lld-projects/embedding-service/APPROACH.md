# Design Approach for Embedding Service

A step-by-step thought process for designing the embedding service.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Text | ❌ No | Primitive input — not an entity we model |
| Embedding | ❌ No | Opaque numeric vector — `List[float]` is sufficient |
| Embedding Request | ✅ Yes | Input data carrier with text and optional model name |
| Embedding Result | ✅ Yes | Output data carrier with embedding, metadata, cache flag |
| Embedding Model | ✅ Yes | Abstract interface for pluggable backends |
| Random Model | ✅ Yes | Stub implementation for demos |
| Hash Model | ✅ Yes | Deterministic implementation for testing |
| Cache | ✅ Yes | In-memory store with TTL and eviction |
| Embedding Service | ✅ Yes | Orchestrator combining model, cache, normalization |
| Metrics | ❌ No | Derived from service state — not a standalone entity |

**Final Entities (v1)**: EmbeddingRequest, EmbeddingResult, EmbeddingModel, RandomEmbeddingModel, HashEmbeddingModel, EmbeddingCache, EmbeddingService

---

## Step 2: Define Relationships

```
EmbeddingModel (1) ──used by──> (1) EmbeddingService
EmbeddingCache (1) ──used by──> (1) EmbeddingService
EmbeddingService (1) ──produces──> (n) EmbeddingResult
EmbeddingService (1) ──accepts──> (n) EmbeddingRequest
EmbeddingCache (1) ──stores──> (n) cached embeddings
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| EmbeddingService → EmbeddingModel | Composition | Model injected at construction |
| EmbeddingService → EmbeddingCache | Association | Optional cache injected at construction |
| EmbeddingService → EmbeddingResult | Derivation | Results are produced from inputs |
| EmbeddingCache → embedding vectors | Composition | Cached vectors don't exist outside the cache |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Swap embedding models without changing the service |
| **Proxy** | ✅ Yes | Cache transparently wraps model calls |
| **Factory** | 🔄 v2 | Create models by name |
| **Observer** | 🔄 v2 | Notify listeners on embedding events |
| **Singleton** | ❌ No | No global state — prefer dependency injection |
| **Decorator** | 🔄 v3 | Add quantization or dimension reduction as decorators |

### Pattern Application:

1. **Strategy Pattern** — EmbeddingModel
   - `RandomEmbeddingModel` and `HashEmbeddingModel` implement the same interface
   - `EmbeddingService` delegates embedding generation to whichever model is injected
   - Easy to add `OpenAIEmbeddingModel` or `SentenceTransformerModel` later

2. **Proxy Pattern** — EmbeddingCache
   - The cache sits between the service and the model
   - Cache hits bypass model computation entirely
   - Service works identically with or without a cache

---

## Step 4: Design Classes

### Core Classes:

#### EmbeddingRequest (dataclass)
- **Attributes**:
  - `text: str` — input text to embed
  - `model_name: str` — optional model identifier (default `"default"`)
- **Methods**: None (pure data carrier)

#### EmbeddingResult (dataclass)
- **Attributes**:
  - `text: str` — original input text
  - `embedding: List[float]` — computed vector
  - `model_name: str` — producing model
  - `dimensions: int` — vector dimensionality
  - `cached: bool` — whether result came from cache
- **Methods**: None (pure data carrier)

#### EmbeddingModel (ABC)
- **Properties**:
  - `model_name: str` — identifier
  - `dimensions: int` — output dimensionality
- **Methods**:
  - `embed(text) → List[float]` — abstract, one text
  - `embed_batch(texts) → List[List[float]]` — default sequential implementation

#### RandomEmbeddingModel
- **Attributes**: `_dimensions: int` (default 128)
- **Embed logic**: `random.random()` for each dimension
- **Non-deterministic**: Different result each call

#### HashEmbeddingModel
- **Attributes**: `_dimensions: int` (default 128)
- **Embed logic**: SHA-256 of text → expand bytes to fill all dimensions
- **Deterministic**: Same text → same embedding every time

#### EmbeddingCache
- **Attributes**:
  - `_cache: dict` — key → (embedding, timestamp)
  - `_max_size: int` — capacity limit
  - `_ttl_seconds: float` — expiry duration
  - `_hits: int`, `_misses: int` — counters
- **Methods**:
  - `get(key)` — return embedding or None, incrementing hit/miss counters
  - `put(key, embedding)` — store with timestamp, evict oldest if full
  - `clear()` — reset everything
  - `stats()` — return metrics dict

#### EmbeddingService
- **Attributes**:
  - `_model: EmbeddingModel`
  - `_cache: Optional[EmbeddingCache]`
  - `_total_embeddings: int`
- **Methods**:
  - `embed(text)` — validate → cache check → model.embed → normalize → cache store → return result
  - `embed_batch(texts)` — validate all → embed each → return list of results
  - `normalize_embedding(embedding)` — L2 normalization
  - `get_stats()` — aggregate metrics

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty string as input text
- Whitespace-only string as input text
- Very long text strings (accepted but may be slow)
- None or non-string inputs

### Business Logic:
- Cache hit returns same embedding without recomputation
- Cache miss triggers model call and caches the result
- Expired cache entries are treated as misses
- Cache at capacity evicts oldest entry before inserting
- Batch with mix of cached and uncached texts
- Zero-vector embedding (all zeros) — normalization should handle gracefully

### Boundary Conditions:
- Cache TTL of 0 (immediate expiry — effectively no caching)
- Cache max_size of 0 (no caching)
- Single-dimension embeddings
- Batch of size 1 (should behave like single embed)
- Batch with duplicate texts (should all use cache after first)

---

## Step 6: Optimization Opportunities

### Data Structures:

| Operation | v1 Basic | v3 Optimized |
|-----------|----------|--------------|
| Cache lookup | O(1) dict | O(1) dict |
| Cache eviction | O(n) scan | O(1) OrderedDict |
| Single embed | O(d) | O(d) |
| Batch embed (k) | O(k · d) | O(k · d) parallel |
| Normalization | O(d) | O(d) |

*d = embedding dimensions, n = cache size, k = batch size*

### Caching:
- Cache key: `f"{model_name}:{text}"` for model-specific caching
- Pre-normalized embeddings stored in cache (avoid re-normalizing on hits)

### Batch Processing:
- v1: Sequential iteration over texts
- v3: Parallel processing with thread pool or async

---

## Step 7: Version Progression

### v1-basic
- Two stub model backends (random, hash)
- In-memory cache with TTL and oldest-entry eviction
- L2 normalization on all outputs
- Input validation with descriptive errors
- Basic metrics (embedding count, cache stats)

### v2-extended
- Model factory for creating backends by name
- Embedding truncation and padding for dimension alignment
- Async batch processing
- Cache persistence (JSON serialization to file)
- Cosine similarity utility method

### v3-optimized
- Connection pool for remote model backends
- LRU eviction with `collections.OrderedDict`
- Cache sharding for concurrent access
- Streaming batch embeddings (yield results as computed)
- Embedding quantization stubs (float32 → int8)

---

## Code Organization

```
embedding-service/
├── PROBLEM.md                  # Requirements and constraints
├── APPROACH.md                 # This design walkthrough
├── DESIGN.md                   # Class diagrams and decisions
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py         # Package marker
│   │   ├── embedding_model.py  # EmbeddingModel ABC, Request/Result dataclasses, stub models
│   │   ├── cache.py            # EmbeddingCache with TTL and eviction
│   │   ├── service.py          # EmbeddingService orchestrator
│   │   └── demo.py             # Runnable end-to-end example
│   └── tests/
│       ├── __init__.py         # Package marker
│       └── test_embedding_service.py  # Unit tests for all components
```

---

## Interview Discussion Points

1. **Why Strategy for Embedding Models?**
   - Production systems swap between local and remote models
   - Callers inject the model they need without touching service code
   - Follows Open/Closed Principle — add an `OpenAIModel` tomorrow

2. **Why a Separate Cache Class?**
   - Caching is a cross-cutting concern independent of embedding logic
   - The service works identically with or without caching
   - Cache policy (TTL, eviction) can evolve independently of the model

3. **Why L2 Normalization?**
   - Normalized vectors enable cosine similarity via dot product
   - Consistent output simplifies downstream consumers (indexes, similarity search)
   - Industry standard for embedding services

4. **How would you add a real model backend?**
   - Implement a new `EmbeddingModel` subclass (e.g., `OpenAIEmbeddingModel`)
   - Handle API authentication, rate limiting, and retries in the subclass
   - No changes to `EmbeddingService` or `EmbeddingCache`

5. **How would you scale the cache?**
   - Replace in-memory dict with Redis or Memcached
   - Add cache sharding by text hash for distribution
   - Implement LRU or LFU eviction for better hit rates
