# Interview Questions: Elasticsearch

## Basic Questions

### 1. Why use Elasticsearch when we already have SQL indexes?
**Q**: What practical gap does Elasticsearch fill in interview-scale systems?

**A**: Elasticsearch is optimized for relevance-driven retrieval (full-text ranking, faceting, aggregations, autocomplete, geo search / geospatial filtering). SQL indexes are excellent for transactional lookups and strict filtering, but become costly for high-cardinality text relevance plus rich filtering at large scale.

### 2. Is Elasticsearch a source of truth?
**Q**: Can we write business-critical constraints directly to Elasticsearch?

**A**: No. Keep OLTP data stores as source of truth for invariants and transactional writes. Elasticsearch should be treated as a read-optimized projection.

### 3. What are shards and replicas?
**Q**: Explain them in interview terms.

**A**:
- **Shard**: logical partition of index data.
- **Replica**: copy of shard for availability and read scaling.
- More shards are not always better; oversharding increases coordination and memory overhead.

## Intermediate Questions

### 4. How do you model local business search (Yelp-style)?
**Q**: We need search by term, category, and location with low latency. How do you model and query?

**A**:
- Index business documents with:
  - text fields (`name`, `description`, `categories`)
  - `geo_point` (`location`)
  - ranking signals (`avg_rating`, `review_count`, `is_open`)
- Query with `bool`:
  - `must`: text query (`multi_match`)
  - `filter`: category/status constraints
  - `geo_distance`: radius bound
- Rank with `function_score`: text relevance + distance decay + quality boosts.

### 5. How do you support location-name search (city/neighborhood) instead of lat/lng?
**Q**: Users type "Mission District" or "Seattle downtown". What do you do?

**A**:
- Resolve location name to polygon or centroid using a location metadata service.
- Use two-stage narrowing:
  - coarse filter by location identifiers/polygon bounding area
  - precise geo filter + ranking
- Keep fallback behavior when polygon resolution fails (centroid radius search).

### 6. How do you keep p95 search latency low?
**Q**: Search is timing out at p95/p99. What first actions do you take?

**A**:
- Move non-scored clauses to `filter` context.
- Reduce payload size (`_source` filtering).
- Tune analyzers and remove unnecessary wildcard patterns.
- Revisit shard sizing and segment merge pressure.
- Add request cache for repeated filtered queries.

### 7. How do you handle one-review-per-user constraints in a Yelp-like system?
**Q**: Should uniqueness be enforced in Elasticsearch?

**A**:
- Enforce uniqueness in OLTP via `(business_id, user_id)` unique key.
- Keep Elasticsearch as projection of aggregate/search fields.
- Use idempotent write API to handle retries safely.

## Advanced Questions

### 8. How do you keep rating aggregates fresh in search results?
**Q**: We show `avg_rating` and `review_count` in search cards. How do we maintain them?

**A**:
- Update aggregates in OLTP on each review write.
- Emit change events to indexing pipeline.
- Update business search documents asynchronously.
- Define freshness SLO (for example, "search view converges within a few seconds").
- Run reconciliation jobs to correct drift.

### 9. How do you evolve mappings safely?
**Q**: A field type change is incompatible with current index. What is the migration pattern?

**A**:
1. Create new index with target mapping.
2. Reindex from source-of-truth data.
3. Validate query parity and latency.
4. Swap aliases atomically.
5. Keep rollback alias for fast recovery.

### 10. Multi-tenant Elasticsearch in shared clusters
**Q**: How do you prevent noisy neighbors?

**A**:
- Tenant-aware routing/index partition strategy.
- Quotas (QPS, index size, refresh/load limits).
- Lifecycle policies by tenant tier.
- Per-tenant observability and throttling controls.

## Common Follow-ups

- When should you denormalize vs join at query time?
- How do analyzers differ for autocomplete vs full-text relevance?
- How do you choose shard count at launch and adjust later?
- How do you measure relevance quality, not just latency?

## Red Flags to Avoid

- Treating Elasticsearch as transactional source of truth.
- Promising strict real-time consistency without an indexing freshness contract.
- Enforcing hard invariants (like review uniqueness) in projection/search layer.
- Oversharding early without throughput evidence.

## 30-Second Explanation

"Elasticsearch is my search and ranking projection, not my transactional source of truth. I write invariants to OLTP, project to Elasticsearch asynchronously, and optimize queries with filter context plus relevance scoring. For local business search, I combine text relevance with geo distance and quality signals while maintaining a bounded freshness SLO."

---

### Social-search freshness follow-up

Q: Why not index synchronously on post write?
A: Async indexing protects write latency and availability; freshness is handled as an explicit SLO.
