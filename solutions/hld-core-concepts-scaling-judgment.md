# Coach Answer: Core Concepts Scaling Judgment (HLD)

Type: High-Level Design (Concept Drill)
Difficulty: Advanced
Time Target: 45 minutes

---

## Phase 1 - Requirements Clarification (5 min)

Functional goal:
- Propose a resilient architecture for a growing product API with mixed workloads.

Non-functional targets:
- p99 read latency < 120 ms
- write correctness for transactional actions
- 99.95% availability for browse/read paths

Constraints:
- Multi-region deployment
- rapid growth expected over 12 months
- avoid premature complexity

Out of scope:
- detailed provider-specific capacity pricing
- implementation-level code

---

## Phase 2 - Capacity Framing (5 min)

Working assumptions:
- 20k read req/sec, 2k write req/sec
- read-heavy browse paths, smaller set of critical write paths
- dataset growth from ~5 TB to ~40 TB over horizon

Decision impact:
- single primary + replicas is acceptable in early stage
- sharding is planned as a trigger-based evolution, not day-one default

---

## Phase 3 - CAP Policy by Operation (7 min)

Consistency-first:
- booking/payment/inventory claim endpoints
- behavior: reject/defer when quorum cannot guarantee correctness

Availability-first:
- listing/feed/search-browse endpoints
- behavior: allow bounded staleness with clear freshness contract

Rationale:
- avoid irreversible double-commit errors on critical writes
- preserve user-facing availability on non-critical reads

---

## Phase 4 - Data Scaling Strategy (10 min)

Stage 1:
- optimize schema and indexes
- add cache-aside for hot reads
- add read replicas

Stage 2 triggers:
- sustained write pressure near single-primary headroom
- backup/restore windows exceed operational targets
- rising p99 due to dataset/index growth

Stage 2 execution:
- pick high-cardinality shard key aligned to dominant query filters
- start hash/consistent-hash sharding for point lookup heavy access
- avoid frequent cross-shard fan-out on latency-sensitive paths

Migration safety:
- dual writes
- checkpointed backfill
- staged read cutover
- parity checks + rollback gates

---

## Phase 5 - Consistent Hashing and Hotspot Control (8 min)

Consistent hashing goals:
- bounded remap during node add/remove
- stable ownership as cluster changes

Important caveat:
- consistent hashing solves ownership churn, not popularity skew

Hotspot mitigation stack:
- read from replicas for hot keys
- key bucketing/salting when semantics allow
- local cache + single-flight miss control
- targeted rate limiting/admission control

---

## Phase 6 - Trade-offs and Wrap-up (10 min)

Key decisions:
- defer sharding until measured trigger metrics
- choose operation-level CAP policy
- use consistent hashing for scale events, plus separate hotspot controls

Trade-off language:
- "I accept bounded staleness on browse reads to preserve availability."
- "I reject uncertain critical writes during partition to protect correctness."
- "I add sharding only after proving indexing, caching, and replicas are insufficient."

---

## Scoring Breakdown

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements and scope | 15% | Clear critical vs non-critical flows |
| Estimation relevance | 15% | Numbers tied directly to architecture decisions |
| CAP decision quality | 20% | Endpoint-level policy, not global label |
| Data scaling plan | 20% | Trigger-based evolution with migration safety |
| Hotspot/failure handling | 15% | Explicit mitigation stack and degraded modes |
| Communication | 15% | Crisp trade-off statements and coherent close |

Score guide:
- 85-100: strong hire-level reasoning
- 70-84: solid with some missing depth
- <70: too generic or missing operational safety

---

## Common Mistakes

1. Jumping to sharding without trigger metrics
2. Saying "system is AP" or "system is CP" globally
3. Assuming consistent hashing alone solves hot keys
4. No migration rollback criteria
5. No freshness contract for stale-allowed endpoints

---

## Follow-up Variants

1. Variant A: sudden hot-key incident during peak event traffic
2. Variant B: region partition during payment peak
3. Variant C: shard-key migration due to query pattern shift
4. Variant D: strict data residency requirement by geography

---

## One-minute closing script

"I chose operation-level CAP behavior: correctness-first for critical writes, availability-first for browse paths with bounded staleness. I start with indexing, cache, and replicas, and only introduce sharding once measurable triggers are sustained. For scale events I use consistent hashing with vnodes for bounded remap, and separately handle traffic hotspots with replica reads, key bucketing, and cache protections. Migration is treated as a first-class workflow with dual writes, checkpointed backfill, staged cutover, and rollback gates."
