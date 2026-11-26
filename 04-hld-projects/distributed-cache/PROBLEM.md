# Distributed Cache System

## Problem Statement

Design a distributed in-memory cache supporting `set/get/delete`, TTL, and eviction while meeting low-latency and high-availability goals at large scale.

---

## Requirements and Constraints

### Functional Requirements

1. Users can set, get, and delete key-value pairs.
2. Keys can have optional TTL.
3. System evicts stale keys using LRU as default policy.
4. Clients can continue read/write operations during node changes.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Get/Set latency | < 10 ms P99 |
| Availability | 99.99% |
| Consistency model | Eventual acceptable |
| Throughput | 100K+ requests/sec |
| Working set | ~1 TB total |

### Capacity Assumptions

- 100K peak requests/sec.
- 1 TB logical data size.
- Hot-key skew expected.
- Node membership changes during scale events.

### Out of Scope

- Full transactional semantics.
- Cross-key ACID guarantees.
- Rich secondary-query capabilities.

---

## High-Level Design Outline

### Core Services

- Cache Router SDK / Proxy
- Cache Node Service
- Membership and Health Service
- Rebalance Service
- Metrics and Hot-Key Detector

### API Surface (Illustrative)

```http
PUT /api/v1/cache/{key}
GET /api/v1/cache/{key}
DELETE /api/v1/cache/{key}
```

---

## Scoring Rubric (Quick Signals)

1. Correct partitioning/routing strategy.
2. Hot-key mitigation and rebalance safety.
3. Clear eviction + TTL behavior under memory pressure.
4. Explicit failure-mode behavior during node outages.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Modulo-based routing with full remap on membership changes.
- Ignoring hot-key concentration.
- Treating cache as strongly consistent source of truth.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do we rebalance with minimal cache miss blast radius?
- How do we handle hot writes for a single key?
- How do we reduce tail latency during failover?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Write-through mode for selected keys.
- Multi-region read-local caching.
- Tiered in-process + remote cache.

---

## Related Links

- [DESIGN](./DESIGN.md)
- [APPROACH](./APPROACH.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
- [03-hld-concepts/consistent-hashing](../../03-hld-concepts/consistent-hashing/)
- [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/)
