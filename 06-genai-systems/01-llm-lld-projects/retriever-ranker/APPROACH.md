# Design Approach for Retriever–Ranker Pipeline

A step-by-step thought process for designing the retrieval-and-ranking pipeline.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| Retrieval Result | ✅ Yes | Core data carrier — a single search hit with score and metadata |
| Ranked Result Set | ✅ Yes | Ordered collection of results returned to callers |
| Retriever | ✅ Yes | Abstract interface for fetching candidates from an index |
| Dense Retriever | ✅ Yes | Concrete retriever using cosine similarity over vectors |
| Sparse Retriever | ✅ Yes | Concrete retriever using keyword/TF-IDF matching |
| Hybrid Retriever | ✅ Yes | Composite retriever blending dense and sparse results |
| Ranker | ✅ Yes | Abstract interface for ordering results |
| Score Ranker | ✅ Yes | Sorts by raw relevance score |
| Round-Robin Ranker | ✅ Yes | Interleaves results from multiple sources |
| Weighted Ranker | ✅ Yes | Applies source-specific weights before sorting |
| Pipeline | ✅ Yes | Chains retriever → ranker into one call |
| Embedding | ❌ No | Opaque numeric vector — not an entity we own |
| Query | ❌ No | Input parameter, not a persisted entity |
| Metadata | ❌ No | Flat dict on results — not a separate entity |

**Final Entities (v1)**: RetrievalResult, RankedResultSet, Retriever (ABC), DenseRetriever, SparseRetriever, HybridRetriever, Ranker (ABC), ScoreRanker, RoundRobinRanker, WeightedRanker, RetrievalPipeline

---

## Step 2: Define Relationships

```
Retriever (1) ──produces──> (n) RetrievalResult
HybridRetriever (1) ──composes──> (2) Retriever  (dense + sparse)
Ranker (1) ──orders──> (n) RetrievalResult
Ranker (1) ──produces──> (1) RankedResultSet
RetrievalPipeline (1) ──chains──> (1) Retriever + (1) Ranker
RankedResultSet (1) ──contains──> (n) RetrievalResult
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| Retriever → RetrievalResult | Production | Retriever produces result candidates |
| HybridRetriever → Retriever | Composition | Hybrid composes dense + sparse retrievers |
| Ranker → RetrievalResult | Consumption | Ranker consumes and reorders results |
| Ranker → RankedResultSet | Production | Ranker outputs an ordered result set |
| Pipeline → Retriever | Composition | Pipeline owns a retriever |
| Pipeline → Ranker | Composition | Pipeline owns a ranker |
| RankedResultSet → RetrievalResult | Aggregation | Result set holds ordered results |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Strategy** | ✅ Yes | Swap retrieval and ranking algorithms independently |
| **Composite** | ✅ Yes | HybridRetriever composes multiple retrievers behind the same interface |
| **Template Method** | ✅ Yes | Common retrieve flow (validate → fetch → normalize) with varying fetch logic |
| **Factory** | 🔄 v2 | Build retrievers/rankers by name — defer to v2 |
| **Observer** | ❌ No | No event-driven needs in v1 |
| **Singleton** | ❌ No | No global state — prefer dependency injection |
| **Builder** | 🔄 v2 | Complex pipeline assembly with filters — defer to v2 |

### Pattern Application:

1. **Strategy Pattern** — Retriever & Ranker
   - `DenseRetriever`, `SparseRetriever`, `HybridRetriever` implement the `Retriever` interface
   - `ScoreRanker`, `RoundRobinRanker`, `WeightedRanker` implement the `Ranker` interface
   - Callers select strategies at construction time; pipeline delegates to them

2. **Composite Pattern** — HybridRetriever
   - `HybridRetriever` holds references to a dense and a sparse `Retriever`
   - It retrieves from both, merges scores with alpha blending, and returns unified results
   - Callers interact with it through the same `Retriever` interface

3. **Template Method** — Retriever base class
   - Common steps: input validation, retrieval, score normalization, top-k truncation
   - Subclasses override only the core `_fetch` hook
   - Keeps validation and post-processing DRY

---

## Step 4: Design Classes

### Core Classes:

#### RetrievalResult (dataclass)
- **Attributes**:
  - `chunk_id: str` — unique identifier for the retrieved chunk
  - `content: str` — text content of the chunk
  - `score: float` — relevance score (0.0 to 1.0)
  - `metadata: Dict[str, str]` — key-value annotations
  - `source: str` — which retriever produced this result (e.g., "dense", "sparse")
- **Methods**: None (pure data carrier)

#### RankedResultSet (dataclass)
- **Attributes**:
  - `results: List[RetrievalResult]` — ordered results
  - `total_candidates: int` — total candidates before top-k
- **Methods**:
  - `top(k: int) → RankedResultSet` — return top-k slice

#### Retriever (ABC)
- **Methods**:
  - `retrieve(query, top_k) → List[RetrievalResult]` — public entry point
  - `_fetch(query) → List[RetrievalResult]` — abstract hook for subclasses
- **Implementations**: DenseRetriever, SparseRetriever, HybridRetriever

#### DenseRetriever
- **Attributes**:
  - `_vectors: Dict[str, List[float]]` — chunk_id → embedding
  - `_documents: Dict[str, str]` — chunk_id → content
  - `_metadata: Dict[str, Dict[str, str]]` — chunk_id → metadata
- **Fetch Logic**: Compute cosine similarity between query embedding and all stored vectors

#### SparseRetriever
- **Attributes**:
  - `_corpus: Dict[str, str]` — chunk_id → text content
  - `_metadata: Dict[str, Dict[str, str]]` — chunk_id → metadata
  - `_idf: Dict[str, float]` — term → inverse document frequency (computed on add)
  - `_tf: Dict[str, Dict[str, float]]` — chunk_id → {term → frequency}
- **Fetch Logic**: Compute TF-IDF dot product between query terms and document terms

#### HybridRetriever
- **Attributes**:
  - `_dense: Retriever` — dense retrieval source
  - `_sparse: Retriever` — sparse retrieval source
  - `_alpha: float` — blending weight (0 = sparse-only, 1 = dense-only)
- **Fetch Logic**: Retrieve from both, merge by chunk_id, blend scores linearly

#### Ranker (ABC)
- **Methods**:
  - `rank(results, top_k) → RankedResultSet` — public entry point
- **Implementations**: ScoreRanker, RoundRobinRanker, WeightedRanker

#### ScoreRanker
- **Logic**: Sort by descending score, return top-k

#### RoundRobinRanker
- **Logic**: Group results by source, interleave one from each source in round-robin, truncate to top-k

#### WeightedRanker
- **Attributes**:
  - `_weights: Dict[str, float]` — source name → weight multiplier
  - `_default_weight: float` — weight for unknown sources
- **Logic**: Multiply each result's score by its source weight, then sort descending

#### RetrievalPipeline
- **Attributes**:
  - `_retriever: Retriever` — fetches candidates
  - `_ranker: Ranker` — orders candidates
- **Methods**:
  - `query(query, top_k) → RankedResultSet` — run retrieve → rank

---

## Step 5: Handle Edge Cases

### Input Validation:
- Empty query text or zero-length query embedding
- `top_k` ≤ 0
- Alpha outside [0, 1] range for HybridRetriever
- Empty corpus (no indexed documents)
- Mismatched embedding dimensions in DenseRetriever

### Business Logic:
- Duplicate chunk_id across dense and sparse results in hybrid mode → merge scores
- All results have score 0.0 → maintain original order
- Fewer results than top_k → return all available
- Round-robin with unequal source group sizes → drain shorter groups first
- Weighted ranker with a source not in the weights dict → use default weight

### Boundary Conditions:
- Single document in corpus → always returns that document
- Alpha = 0.0 → hybrid should behave identically to sparse-only
- Alpha = 1.0 → hybrid should behave identically to dense-only
- Query identical to an indexed document → score should be 1.0 (or near 1.0)

---

## Step 6: Optimization Opportunities

### Data Structures:

| Operation | v1 Basic | v3 Optimized |
|-----------|----------|--------------|
| Dense retrieve | O(n · d) brute-force | O(log n) ANN |
| Sparse retrieve | O(n · q) TF-IDF scan | O(q · k) inverted index |
| Score ranking | O(n log n) sort | O(n log k) heap-select |
| Hybrid merge | O(n) dict merge | O(n) dict merge |
| Pipeline end-to-end | O(n · d + n log n) | O(log n + n log k) |

*n = corpus size, d = embedding dimension, q = query terms, k = top-k*

### Caching:
- Cache vector norms to avoid recomputation in cosine similarity
- Cache IDF values (recompute only on corpus update)
- LRU cache for recent query results (v3)

### Indexing:
- Pre-compute and store document TF vectors at index time
- Use inverted index for sparse retrieval (v3)
- Approximate nearest-neighbor indices for dense retrieval (v3)

---

## Step 7: Version Progression

### v1-basic
- DenseRetriever with brute-force cosine similarity
- SparseRetriever with TF-IDF keyword matching
- HybridRetriever with linear alpha blending
- ScoreRanker, RoundRobinRanker, WeightedRanker
- RetrievalPipeline chaining retriever → ranker
- No persistence, no concurrency

### v2-extended
- Metadata-filtered retrieval (pre-filter by key-value)
- Reciprocal-rank fusion as an alternative to alpha blending
- Batch query support
- Result deduplication across sources
- Configurable similarity metrics (cosine, dot product, euclidean)

### v3-optimized
- Approximate nearest-neighbor index stub (LSH or HNSW)
- Async pipeline with `asyncio`
- LRU result cache
- Score explanation (why was this result ranked here?)
- Persistence adapter for index state

---

## Code Organization

```
retriever-ranker/
├── PROBLEM.md                  # Requirements and constraints
├── APPROACH.md                 # This design walkthrough
├── DESIGN.md                   # Class diagrams and decisions
├── python/
│   ├── v1-basic/
│   │   ├── __init__.py         # Package marker
│   │   ├── result.py           # RetrievalResult, RankedResultSet
│   │   ├── retriever.py        # Retriever ABC, Dense, Sparse, Hybrid
│   │   ├── ranker.py           # Ranker ABC, Score, RoundRobin, Weighted, Pipeline
│   │   └── demo.py             # Runnable end-to-end example
│   └── tests/
│       ├── __init__.py         # Package marker
│       └── test_retriever_ranker.py  # Unit tests for all components
```

---

## Interview Discussion Points

1. **Why Strategy for Retrieval?**
   - Different retrieval scenarios need different algorithms (dense vs. sparse vs. hybrid)
   - Callers swap retrieval strategies without touching pipeline or ranking code
   - Follows Open/Closed Principle — add a `SemanticRetriever` tomorrow

2. **Why Composite for Hybrid?**
   - HybridRetriever composes two retrievers behind the same `Retriever` interface
   - Callers don't need to know whether they're using dense, sparse, or hybrid
   - Alpha blending is a simple, well-understood fusion technique

3. **Why not generate real embeddings?**
   - Embedding generation is an infrastructure concern, not a design concern
   - Keeping it as `List[float]` lets us focus on the retrieval/ranking design
   - Callers can plug in any model (OpenAI, Sentence-Transformers, etc.)

4. **How would you add a new vector DB backend?**
   - Implement a new `Retriever` subclass wrapping the DB client
   - Override `_fetch` to delegate to the DB's native search API
   - No changes to rankers, pipeline, or result types
