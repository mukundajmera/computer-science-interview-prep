# Semantic Retrieval Platform - Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Semantic Retrieval Platform project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements & Scope | 10% | Clearly distinguishes retrieval-vs-generation scope (treats platform as retrieval infrastructure, not answer generation). Adheres to existing scope and SLO assumptions. |
| Capacity & Cost Modeling | 10% | Calculates raw capacity (50M chunks × 1536 dims × 4 bytes = 307.2 GB raw decimal, excluding index/replication). Explains bounds on embedding cost and latency. |
| Ingestion & Freshness | 15% | Designs asynchronous indexing queues to meet the < 5 minutes freshness SLA. Discusses document chunking, updates, and reindex lifecycle. |
| Hybrid ANN Retrieval | 20% | Proposes a robust hybrid ANN retrieval API blending dense and keyword signals. Recognizes ANN is approximate (no exact top-k guarantee) and uses optional reranking. |
| ACL Enforcement | 20% | Enforces strict tenant and ACL isolation before returning chunks. Understands that authoritative ACL checks may reduce results, and overfetch is not authorization. |
| Citations & Quality Metrics | 15% | Ensures returned chunks include source traceability for citations. Proposes metrics for retrieval quality (recall@k, MRR/NDCG, empty-hit rate, citation usefulness) and operational health. |
| Migrations | 10% | Defines safe index migration plans (dual index, shadow queries, staged cutover) and handles vector versioning without downtime. |

## Scoring formula

Define `score_i` in 1..5 for each dimension. The overall score is calculated as `weighted_total = sum(score_i * weight_i) / 100`. Weights total 100 and all bands remain on a 1..5 scale.

## Performance bands

- `1/5`: Trivial single-tenant vector database wrapper. Confuses retrieval with final LLM generation. Misses capacity bounds. Fails to understand that ANN is approximate or ignores strict ACL enforcement.
- `3/5`: Basic multi-tenant retrieval platform. Covers ingestion and ANN search. Estimates capacity but misses the nuances of hybrid retrieval. Might rely solely on client-side ACL filtering or misunderstand the impact of ACL on ANN top-k limits.
- `5/5`: Enterprise-grade retrieval platform. Correctly estimates the 307.2 GB raw capacity, enforces authoritative ACL checks acknowledging result reduction, uses hybrid search with reranking, clearly separates retrieval from generation, establishes quality metrics, and plans for safe index migrations.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
