# Retriever–Ranker Pipeline

## Problem Statement

Design a retrieval-and-ranking pipeline that supports dense vector retrieval, sparse keyword retrieval, and hybrid combinations of both. The system should score and rank results with configurable weights while remaining completely agnostic to any specific vector database.

---

## Functional Requirements

1. **Dense Vector Retrieval**: Retrieve documents by cosine similarity over in-memory embedding vectors
2. **Sparse Keyword Retrieval**: Retrieve documents using TF-IDF-like keyword matching against an in-memory corpus
3. **Hybrid Retrieval**: Combine dense and sparse retrieval results with a configurable alpha weight (0 = sparse-only, 1 = dense-only)
4. **Result Scoring**: Score each result with a float between 0.0 and 1.0 representing relevance
5. **Configurable Ranking**: Support multiple ranking strategies — sort-by-score, round-robin interleaving, and weighted multi-source ranking
6. **Metadata Filtering**: Filter retrieval results by key-value metadata before ranking
7. **Top-k Selection**: Return only the top-k most relevant results after ranking
8. **Pipeline Orchestration**: Chain retriever → ranker in a single pipeline entry point

---

## Non-Functional Requirements

1. **DB-Agnostic Abstractions**: Retriever and ranker interfaces must not depend on any specific vector database or search engine
2. **Pluggable Scoring**: New scoring and ranking strategies can be added without modifying existing classes (Open/Closed Principle)
3. **Stateless Retrieval Pipeline**: The pipeline itself holds no mutable state between queries; all state lives in the index
4. **Testability**: Every component must be independently unit-testable with no external dependencies
5. **Standard Library Only**: No external dependencies — use Python's built-in modules exclusively

---

## Constraints & Assumptions

- Embeddings are represented as `List[float]` — the system does **not** generate real embeddings; callers supply them
- Documents are pre-indexed in-memory before retrieval (no persistence layer in v1)
- Cosine similarity is the default dense similarity metric
- Sparse retrieval uses term-frequency / inverse-document-frequency heuristics with simple whitespace tokenization
- Metadata is a flat `Dict[str, str]` on each result
- Score normalization (0–1 range) is best-effort; raw scores from different sources may need re-scaling
- The hybrid alpha parameter blends dense and sparse scores linearly: `score = alpha * dense + (1 - alpha) * sparse`

---

## Sample Interactions

```
1. Caller indexes documents with embeddings and text content
2. Caller creates a DenseRetriever over the in-memory vector store
3. Caller queries: retriever.retrieve(query_embedding, top_k=5) → List[RetrievalResult]
4. Alternatively, SparseRetriever.retrieve(query_text, top_k=5) → keyword-matched results
5. HybridRetriever combines both with alpha=0.7 (70 % dense, 30 % sparse)
6. Results are passed to a Ranker (e.g., ScoreRanker or WeightedRanker)
7. Ranker.rank(results, top_k=3) → RankedResultSet with the final ordered list
8. Pipeline chains steps 2–7 in a single call
```

---

## Clarifying Questions to Ask

1. "What embedding dimensionality should the index expect?"
2. "Should hybrid alpha be fixed at construction or adjustable per query?"
3. "Do we need to support filtered retrieval (e.g., only chunks from a specific source)?"
4. "Is real-time index updates required, or is a static corpus acceptable?"
5. "How should tied scores be broken during ranking?"
6. "Do we need to support pagination beyond top-k?"
7. "Should the ranker be able to explain its ranking decisions (explainability)?"
8. "What is the expected corpus size — hundreds, thousands, or millions of documents?"

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| RetrievalResult | A single retrieval hit with chunk ID, content, score, and metadata |
| RankedResultSet | An ordered collection of ranked results with total count |
| Retriever | Abstract interface for fetching candidate results |
| DenseRetriever | Retrieves candidates via cosine similarity over vectors |
| SparseRetriever | Retrieves candidates via TF-IDF keyword matching |
| HybridRetriever | Combines dense and sparse retrieval with alpha blending |
| Ranker | Abstract interface for ordering retrieval results |
| ScoreRanker | Sorts results by descending score |
| RoundRobinRanker | Interleaves results from multiple ranked lists |
| WeightedRanker | Applies configurable weights to scores from different sources |
| RetrievalPipeline | Chains a retriever and ranker into a single query entry point |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Dense, sparse, and hybrid retrieval; score/round-robin/weighted rankers; pipeline orchestrator; in-memory index |
| v2-extended | Metadata-filtered retrieval, batch queries, reciprocal-rank fusion, configurable similarity metrics, result deduplication |
| v3-optimized | Approximate nearest-neighbor stub, async pipeline, result caching with LRU eviction, score explanation, persistence adapter |
