# Semantic Retrieval Platform - Comparison

## Vector Index Types

| Concern | HNSW | IVF-PQ |
|---|---|---|
| Usage | HNSW is the latency and recall default. | IVF/PQ is an option when memory pressure dominates. |
| Trade-offs | Fast retrieval at the cost of high memory usage. | Compression reduces memory cost but can hurt retrieval quality. Measure recall against a gold set. |

## ACL Filtering Strategies

| Concern | Pre-filter plus candidate validation | Post-filter-only |
|---|---|---|
| Implementation | Metadata is evaluated prior to or during search, then candidates are validated. | Candidates are fetched first, then filtered for access. |
| Characteristics | Stronger isolation and better cost control. | Weaker isolation and potentially wasted retrieval effort. |

ANN is approximate; neither approach guarantees exactly top_k and the authorized corpus can contain fewer than k. ACL filters and authoritative candidate validation protect authorization; they do not guarantee k. Overfetching is not authorization.

## Reranking

| Concern | Optional rerank | Always rerank |
|---|---|---|
| Application | Reranking is optional per request subject to the documented latency, cost, and rerank budgets. | Applying reranking to every request may exceed latency and cost limits. |

## Retrieval Modes

| Concern | Semantic-only retrieval | Hybrid retrieval |
|---|---|---|
| Behavior | Retrieval relies solely on dense vector search. | Uses documented lexical and semantic blend controls. |

## Cross-links

- [Problem Statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
