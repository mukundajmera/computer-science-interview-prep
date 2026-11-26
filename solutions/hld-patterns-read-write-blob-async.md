# Coach Answer: Scaling Patterns (Reads/Writes/Blobs/Async)

Type: High-Level Design (Pattern Drill)
Difficulty: Advanced
Time Target: 45 minutes

---

## Phase 1 - Requirements Clarification (5 min)

Goal:
- Design a platform that serves high-volume reads, sustained writes, large file transfers, and long-running background jobs.

Non-functional targets:
- Read p99 < 150 ms on browse endpoints
- Correctness-first for critical writes
- Upload success with resumability for large files
- 99.95% availability for user-facing APIs

Constraints:
- Multi-region traffic
- Bursty demand windows (3x-10x)
- Mixed workloads (fast requests + heavy tasks)

Out of scope:
- Provider-specific managed-service tuning details

---

## Phase 2 - Capacity Framing (5 min)

Assumptions:
- Read/write ratio around 40:1 on primary product surfaces
- Periodic burst events increase writes 4x
- Media uploads include 10MB to multi-GB files
- Background operations include transcoding, indexing, and moderation

Decision trigger framing:
- Reads: optimize/index/cache before complex repartitioning
- Writes: partition and batch when sustained pressure breaches safe headroom
- Blob transfer: direct storage path once file sizes exceed practical API proxy limits
- Async: queue-worker model whenever operation exceeds request timeout budget

---

## Phase 3 - Architecture Decisions (20 min)

### A) Read Scaling
- Start with index/query tuning and selective denormalization.
- Add read replicas for throughput.
- Add service cache + CDN edge cache for shared content.
- Add stampede protection and hot-key controls.

### B) Write Scaling
- Use partition-aware keys with skew monitoring.
- Use queue buffering for short-lived bursts only.
- Apply batching/aggregation for high-frequency event streams.
- Add backpressure and shedding policy for overload windows.

### C) Large Blob Handling
- Keep metadata in DB and bytes in object storage.
- Issue presigned/signed URLs for direct client upload/download.
- Use multipart transfers for resumability.
- Confirm completion via storage events + reconciliation.

### D) Long-Running Tasks
- Accept quickly, enqueue, return job ID.
- Process with worker pools tuned by job class.
- Add retries, DLQ, idempotency keys, and status endpoints.
- Use transactional outbox where enqueue durability with DB state must be strict.

---

## Phase 4 - Trade-offs and Failure Modes (10 min)

Key trade-offs:
- Bounded staleness vs read latency and origin protection.
- Write visibility delay vs burst absorption and stability.
- Direct blob transfer efficiency vs state synchronization complexity.
- Async throughput vs increased operational complexity.

Failure-mode handling:
- Replica lag: sticky read-after-write routing.
- Hot keys: key fanout + rate controls + targeted caching.
- Multipart orphaning: lifecycle cleanup windows.
- Poison jobs: retry cap + DLQ isolation + alerting.

---

## Scoring Breakdown

| Dimension | Weight | Strong signal |
|---|---:|---|
| Bottleneck identification | 20% | Clear read/write/blob/async trigger recognition |
| Pattern sequencing | 20% | Practical staged evolution, not over-engineered v1 |
| Reliability/failure design | 20% | Explicit lag, stampede, retries, DLQ, reconciliation |
| Trade-off quality | 20% | Endpoint-aware consistency and latency policy |
| Communication | 20% | Structured, quantitative, and concise rationale |

---

## Common Mistakes

1. Jumping straight to sharding without proving baseline limits.
2. Proxying large files through API servers indefinitely.
3. Queueing everything without backpressure or idempotency.
4. Ignoring hot-spot and cache stampede protections.
5. No operational trigger metrics for evolution.

---

## Follow-up Variants

1. Viral read surge on a single object.
2. Black Friday write burst with 10x ingest.
3. 25GB upload failures at poor network quality.
4. Queue backlog growth with mixed job durations.

---

## One-minute closing script

"I split the design by bottleneck class. For reads, I sequence index/replica/cache and enforce endpoint-specific freshness contracts. For writes, I use partition-aware keys, batching, and controlled burst buffering with backpressure. For large blobs, I move bytes off app servers via direct signed transfer and preserve correctness through event-confirmed metadata state plus reconciliation. For long-running tasks, I return quickly, process asynchronously, and harden reliability with idempotency, retry caps, DLQ, and observable queue health."
