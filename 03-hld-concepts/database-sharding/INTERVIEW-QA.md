# Interview Questions: Database Sharding

## Basic Questions

### 1. What is database sharding?
**Q**: What is database sharding and why is it used?

**A**: Sharding splits one logical database into multiple physical databases so storage and write load can scale horizontally. It is typically introduced when a single primary plus replicas can no longer meet throughput, size, or operational constraints.

### 2. How do you choose a shard key?
**Q**: What makes a shard key strong versus risky?

**A**: A strong shard key is high-cardinality, evenly distributed, and present in common query filters. A risky key is low-cardinality or write-skewed (for example, timestamp-only keys).

### 3. Hash vs range sharding?
**Q**: Compare hash-based and range-based approaches.

**A**:

| Aspect | Hash-based | Range-based |
|---|---|---|
| Distribution | Usually even | Can skew under hotspot ranges |
| Range queries | Weak | Strong |
| Re-sharding | Harder with modulo | Easier to split/merge ranges |
| Typical use | Point lookups | Time/range-heavy workloads |

### 4. Partitioning vs sharding?
**Q**: Are they the same?

**A**: Not exactly. Partitioning usually means splitting data inside one DB instance. Sharding means splitting across independent DB instances.

### 5. What is the hotspot/celebrity problem?
**Q**: Why can one shard overload even with good distribution?

**A**: Traffic distribution and key distribution differ. A few keys can dominate traffic. Mitigations: read replicas for hot keys, key bucketing/salting, selective isolation, and caching.

## Intermediate Questions

### 1. How do you handle cross-shard joins?
**Q**: What is the practical strategy for cross-shard data access?

**A**:
1. Design to co-locate related entities.
2. Use denormalized projections for hot read paths.
3. Use async aggregation for global dashboards.
4. Reserve scatter-gather for rare administrative flows.

### 2. How do you handle distributed transactions?
**Q**: How do you maintain correctness across shards?

**A**: Prefer avoiding cross-shard ACID boundaries via key design. If unavoidable, use saga-style compensation and idempotent steps. 2PC is possible but often high-latency and operationally fragile.

### 3. How do you scale shards without downtime?
**Q**: Describe an online re-sharding process.

**A**:
1. Add destination shards.
2. Dual-write old and new placement.
3. Backfill historical data with checkpoints.
4. Shift reads gradually.
5. Validate and cut over.
6. Keep rollback window until confidence threshold is met.

### 4. How does shard-aware routing work?
**Q**: Where should routing logic live?

**A**: Client-side routing is simple but tightly coupled. Proxy routing centralizes policy. Directory-based routing enables flexible placement but adds a critical dependency.

### 5. How do you support non-shard-key queries?
**Q**: What if the query filter does not include the shard key?

**A**: Use a global index, replicated lookup table, or external search index. Avoid frequent scatter-gather on latency-sensitive paths.

## Scenario Questions

### 1. Hotspot triage
**Q**: One shard is at 95% CPU while others are <35%. What do you do first?

**A**:
1. Confirm whether skew is key-skew or traffic-skew.
2. Add short-term protection: cache, replica reads, rate limits.
3. Apply structural fix: isolate hot keys, bucket keys, or split shard range.
4. Add alerts on shard skew and tail latency to prevent recurrence.

### 2. Cross-shard fallback for global queries
**Q**: Product asks for "top 100 globally" every second. How do you avoid expensive fan-out reads?

**A**: Precompute global rankings asynchronously into a materialized store and serve from cache. Use bounded staleness (for example 10-30 seconds) unless strict real-time correctness is mandatory.

### 3. Shard-key migration
**Q**: How do you move from `user_id` sharding to `tenant_id` sharding safely?

**A**: Introduce versioned routing, dual-write both schemes, backfill with checkpoints, verify row parity and read parity, then switch reads by cohort before final cutover.

## Advanced Questions

### 1. Multi-tenant sharding strategy
**Q**: How do you shard a SaaS with mixed tenant sizes?

**A**: Use hybrid placement: large tenants on dedicated shards, long-tail tenants pooled. Maintain migration tooling to promote/demote tenants as they grow.

### 2. Failure-mode design
**Q**: A shard is unhealthy during peak traffic. How do you preserve service?

**A**: Route reads to healthy replicas, shed non-critical traffic, disable expensive fan-out APIs, and prioritize write-path durability plus recovery backlog draining.

### 3. Re-sharding safety metrics
**Q**: Which metrics decide whether migration can continue?

**A**: Data parity mismatches, replication lag, P99 latency impact, write error rate, and retry amplification.

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Names sharding strategy without risk discussion |
| 3 | Explains key choice and one migration/failure strategy |
| 5 | Quantifies triggers, addresses hotspots, migration, rollback, and observability |

## Common follow-ups

1. How do backups and restores change after sharding?
2. How do you avoid hot partitions in time-series workloads?
3. What is your per-shard SLO and alerting strategy?
4. How do you test migration plans before production cutover?
5. What is your emergency rollback trigger?

## Red flags to avoid

- "We'll just shard" with no trigger metric
- No plan for re-sharding or shard-key change
- Treating cross-shard joins as normal path
- Ignoring idempotency in migration and dual writes
- Not separating availability controls from consistency guarantees

## Strong verbal answers

### 45-second version
"I would shard only after proving replicas and indexing are not enough. I would choose a high-cardinality key aligned with dominant query filters, usually hash-based or consistent hashing for point lookups. I would minimize cross-shard queries with denormalized projections and async aggregates. For growth, I would run online re-sharding using dual writes, checkpointed backfill, and staged read cutover with rollback gates."

### 2-minute version
"My default is to delay sharding until we see sustained trigger metrics such as write throughput saturation, dataset growth beyond practical single-node operations, or unacceptable backup windows. For key selection, I optimize for distribution and query locality: high-cardinality and common filter usage. If the workload is point lookup heavy, I use hash-based placement with a strategy that supports bounded movement during scaling. If range scans dominate, I use range sharding with split/merge tooling and hotspot controls.

Operationally, I treat migration as a product feature: versioned routing, dual writes, checkpointed backfill, parity checks, and staged read cutover. I avoid cross-shard transactions by design, using saga compensation when unavoidable. For failure handling, I rely on per-shard replication, load shedding for non-critical paths, and strict observability on skew, lag, and P99 latency."

## Related concepts

- [Database Sharding Theory](./THEORY.md)
- [Consistent Hashing](../consistent-hashing/)
- [CAP Theorem](../cap-theorem/)
- [Pattern Selection](../pattern-selection/)
