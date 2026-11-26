# Interview Questions: Pattern Selection

## Basic Questions

### 1. How do you choose your first pattern in a new design problem?
**A:** Identify the highest-risk requirement (latency, throughput, consistency, durability, or cost). Pick the simplest pattern that addresses that risk and defer advanced patterns until justified.

### 2. When is caching a good default?
**A:** Caching is a good default when reads are frequent, repeated, and latency-sensitive, and moderate staleness is acceptable.

### 3. When should you use queue + worker instead of synchronous processing?
**A:** Use async jobs when task duration exceeds acceptable request latency or workloads are bursty and need smoothing.

### 4. What is a reliable signal that sharding is needed?
**A:** Consistent evidence that a single primary cannot meet write/storage growth after indexing, query tuning, and replica strategy are already applied.

### 5. How do you answer eventual consistency trade-offs?
**A:** Tie staleness to user impact. If temporary staleness does not break business correctness, eventual consistency can improve availability and latency.

---

## Intermediate Questions

### 6. How do you handle contention on scarce resources (for example last ticket)?
**A:** Begin with transactional updates plus optimistic concurrency checks. Escalate to serialized queueing or distributed locking only when needed.

### 7. How do you prevent cache stampede?
**A:** Combine request coalescing (single-flight), jittered TTLs, and background refresh for hot keys.

### 8. How do you pick between SSE and WebSockets?
**A:** Use SSE for server-to-client push when client messaging is minimal. Use WebSockets for true bidirectional low-latency messaging.

### 9. How do you scale writes without immediate full sharding?
**A:** Use batching, idempotent retries, append-friendly schemas, and partition-aware keys. Add queue buffering for bursts.

### 10. How do you keep multi-step workflows consistent?
**A:** Use saga orchestration/choreography with compensating actions, idempotency keys, and durable state transitions.

---

## Advanced Questions

### 11. How do you explain pattern evolution from v1 to v3?
**A:** v1: simplest reliable baseline; v2: bottleneck-focused optimizations (cache, queue, index); v3: structural scaling changes (sharding, region strategy, workflow partitioning).

### 12. How do you justify not using an advanced pattern?
**A:** State expected scale, current bottleneck, and operational cost. If the pattern adds complexity without removing a proven risk, defer it.

---

## Rapid Follow-up Drill

1. Which pattern would you remove first to simplify v1?
2. Which metric would trigger your next pattern upgrade?
3. Which failure mode is still unaddressed?
4. What is your rollback plan if the chosen pattern fails in production?
