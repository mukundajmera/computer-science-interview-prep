# Embedding Service — Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Embedding Service project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies embedding dimension, batching constraints, caching TTL, and normalization requirements. |
| Domain model quality | 25% | Clean abstraction of `EmbeddingModel`, `EmbeddingCache`, `EmbeddingService`, and metric trackers. |
| Batching & Caching correctness | 25% | Robust cache key hashing, TTL expiration, capacity eviction, and efficient batch deduction. |
| Normalization & Math | 20% | Proper L2 normalization, handling of zero vectors and floating point precision. |
| Extensibility & Tests | 15% | Uses Strategy pattern for models, deterministic mock model for testing, zero third-party deps. |

## Performance bands

- `1/5`: Tightly coupled code directly calling an external API without caching, normalization, or abstractions.
- `3/5`: Implements basic caching and service class, but lacks clean interfaces or correct batch cache deduction.
- `5/5`: Elegant Strategy pattern for models, thread-safe ready, O(1) cache with TTL and LRU/FIFO eviction, deterministic tests.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
