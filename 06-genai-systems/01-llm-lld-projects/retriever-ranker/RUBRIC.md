# Retriever–Ranker - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies retrieval types (dense vector, sparse keyword/BM25), reciprocal rank fusion (RRF), cross-encoder re-ranking. |
| Domain model quality | 25% | Clean abstraction of `Retriever`, `Ranker`, `ScoredDocument`, and hybrid pipeline orchestrator. |
| Algorithmic correctness | 25% | Correct implementation of Reciprocal Rank Fusion ($1/(k + rank)$), deduplication by document ID, score normalization. |
| Performance & Scaling | 20% | Two-stage architecture: fast candidate retrieval ($K_1=50$) followed by compute-intensive re-ranking ($K_2=5$). |
| Extensibility & Tests | 15% | Strategy pattern for retrievers and rerankers, clean deterministic tests verifying ranking order, zero external dependencies. |

## Performance bands
- `1/5`: Single naive keyword or distance search without re-ranking or score combination.
- `3/5`: Implements both dense and sparse retrieval, but simple linear score addition without normalization or RRF.
- `5/5`: Clean two-stage hybrid retrieval with Reciprocal Rank Fusion, pluggable re-rankers, robust deduplication, comprehensive unit tests.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
