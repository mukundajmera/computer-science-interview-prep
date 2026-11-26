# Database Sharding

Database sharding is a horizontal scaling strategy that splits one logical dataset across multiple database servers.

## What is it?

Sharding distributes rows across independent databases (shards) using a shard key. Each shard has its own compute, memory, storage, and connection limits.

## Why do we need it?

A single database eventually hits practical limits:
- Storage growth (data size and index size)
- Write throughput bottlenecks
- Operational limits (backup window, maintenance, failover)

Sharding lets you scale capacity and write throughput by adding shards, but it adds routing and operational complexity.

## Partitioning vs sharding

- Partitioning: split data inside one database instance.
- Sharding: split data across multiple database instances.

You often start with partitioning and replicas before moving to sharding.

## Types/Approaches

### 1. Horizontal sharding
Split rows by shard key (most common).

### 2. Vertical sharding
Split tables/services by domain boundary.

### 3. Directory-based sharding
Use a mapping service (`entity_id -> shard`) for custom placement.

## Sharding strategies

### Hash-based
`shard = hash(key) % N`
- Pros: even spread for point lookups
- Cons: modulo-based re-sharding can move many keys

### Range-based
Assign contiguous key ranges to shards.
- Pros: good range scans
- Cons: skew and hot ranges

### Geo-based
Assign by region/tenant locality.
- Pros: lower regional latency, residency control
- Cons: expensive cross-region joins/queries

### Consistent hashing
Place shards on a ring with virtual nodes.
- Pros: bounded key movement on membership change
- Cons: higher routing complexity

## Requirements and constraints

Before committing to sharding, lock these decisions:
- Data access shape: point lookup, range scans, global aggregates
- Correctness requirements: strict transactions vs eventual consistency
- Growth profile: write-heavy, read-heavy, or archival-heavy
- Operator maturity: rebalancing, migration, incident response
- Failure model: shard loss, network partitions, AZ/region failure

## How it works

### Shard key selection
A good shard key is:
- High-cardinality
- Evenly distributed
- Aligned with common query filters
- Stable over entity lifetime

Risky keys include low-cardinality flags and write-time timestamps that create hot shards.

### Request routing
Typical patterns:
- Client-side routing
- Proxy/middleware routing
- Directory service routing

### Cross-shard queries
Cross-shard fan-out is expensive. Prefer:
- Denormalized projections for hot reads
- Precomputed aggregates
- Cached global views for non-critical freshness

## Rebalancing and online re-sharding

### Online re-sharding playbook
1. Define target topology and movement budget.
2. Provision destination shards and replication.
3. Start dual writes and checkpointed backfill.
4. Gradually cut reads to new placement.
5. Validate checksums/lag, then finalize cutover.

### Migration guardrails
- Throttle migration traffic to protect P99 latency
- Use idempotent copy jobs
- Monitor per-shard skew, replication lag, and error rates
- Keep rollback path until post-cutover validation passes

## When to use

Use sharding when at least one is sustained:
- Single-node storage nearing practical limits
- Write throughput persistently beyond safe headroom
- Operational windows (backup/restore/maintenance) no longer acceptable
- Mandatory geo/data residency boundaries

## When NOT to use

Avoid sharding when:
- Scale still fits a single primary + replicas
- Most critical queries are cross-entity global scans
- Team cannot support operational complexity yet

## Scoring rubric

| Score | Interview signal |
|---|---|
| 1 | Says "we shard" without trigger metrics |
| 3 | Picks a shard key and routing approach with partial trade-offs |
| 5 | Quantifies trigger, justifies key, explains migration/failure plan |

## Common pitfalls

- Premature sharding before indexing/replicas/caching
- Choosing shard key without query-shape alignment
- Ignoring hot-key and hot-range mitigation
- No plan for re-sharding or shard-key migration
- Treating cross-shard transactions as free

## Follow-up questions

1. Which metric tells you your key distribution is failing?
2. How do you migrate shard key without downtime?
3. What is your fallback for expensive cross-shard queries?
4. How do you isolate and recover from one bad shard?
5. What is your rollback plan during cutover?

## Variants and extensions

- Multi-tenant hybrid: dedicated shards for large tenants, pooled shards for long tail
- Time-partition + hash composite: reduce write hotspots while keeping range retention
- Read/write split per shard with quorum choices per endpoint
- Analytics sidecar pipeline for global query offload

## Trade-offs

| Aspect | Benefit | Cost |
|---|---|---|
| Scale | Horizontal growth | More routing and operations |
| Performance | Better write parallelism | Cross-shard fan-out cost |
| Availability | Fault isolation by shard | Per-shard hotspots/failures |
| Flexibility | Independent scaling domains | Migration and consistency complexity |

## GenAI notes

Vector and retrieval systems also face sharding choices:
- Tenant or namespace sharding for isolation
- Semantic/domain sharding for query locality
- Higher reindex cost during re-sharding than row-store migrations

## Related concepts

- [Consistent Hashing](../consistent-hashing/)
- [Database Replication](../database-replication/)
- [CAP Theorem](../cap-theorem/)
- [Pattern Selection](../pattern-selection/)
- [Sharding Theory (Foundations)](../../00-theory/database-concepts/sharding.md)
