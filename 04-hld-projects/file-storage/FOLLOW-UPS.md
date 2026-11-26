# File Storage — Follow-Up Questions

## 1. How do you support very large files reliably?

Use multipart or chunked upload sessions with per-part checksums, resumability, and session expiration with garbage cleanup.

## 2. How do you detect and resolve sync conflicts?

Track file version vectors (or version numbers + base revision), then apply conflict-copy policy for ambiguous merges.

## 3. How do you support selective sync?

Store per-device folder selection and use placeholders for unsynced files with on-demand download.

## 4. How do you improve durability beyond single-region defaults?

Enable cross-region replication for content and continuous backup + PITR for metadata.

## 5. How do you optimize storage costs?

Add block-level dedup, compression, and lifecycle tiering for cold objects.

## 6. How do you support secure sharing links?

Use signed links with expiry, optional password gates, and revocation state checks.

## 7. How do you index files for fast search?

Create async indexing pipeline from metadata and content extraction; keep search decoupled from upload path.

---

## Pattern Integration Addendum

### 7. "How would you choose transport/channel strategy under changing realtime requirements?"

#### Why They Ask

Tests whether you can avoid defaulting to a single transport and instead choose based on interaction model, freshness target, and connection cost.

#### Approach

- **Channel matrix:** Polling for low-frequency updates, long polling for compatibility fallback, SSE for one-way server push, WebSocket for bidirectional high-frequency flows.
- **Fallback policy:** Keep a deterministic downgrade path (`websocket -> sse -> long polling`) for restrictive networks.
- **Ordering + replay:** Assign monotonic event IDs and replay missed ranges after reconnect.
- **Connection management:** Maintain user-to-connection mapping with heartbeat and idle timeouts.

#### Key trade-off

A richer realtime channel improves UX but increases stateful infrastructure complexity and connection operating cost.

### 8. "How would you escalate contention strategy as load and conflict rates increase?"

#### Why They Ask

Probes whether you can pick the least-complex coordination model first, then escalate only when measured conflict pressure justifies it.

#### Approach

- **Start optimistic:** Version-check + bounded retry for low conflict workloads.
- **Escalate selectively:** Move hot keys to pessimistic lock or serialized queue lanes.
- **Distributed coordination:** Use distributed lock only when cross-node exclusivity is truly required.
- **Safety controls:** Add idempotency keys, retry jitter, lock timeout, and deadlock avoidance rules.

#### Key trade-off

Stronger coordination raises correctness confidence but can reduce throughput and availability under peak contention.

### 9. "How would you make multi-step flows durable and retry-safe?"

#### Why They Ask

Tests your ability to keep business consistency across partial failures in workflows that span services and time.

#### Approach

- **State machine first:** Define explicit lifecycle states and transition guards.
- **Saga style:** Commit each step independently with compensating actions for rollback.
- **Durability:** Persist workflow checkpoints before advancing to the next step.
- **Idempotency:** Require stable idempotency keys for all side-effecting steps.
- **Versioning:** Keep old workflow definitions alive for in-flight instances during upgrades.

#### Key trade-off

Durable orchestration improves resilience and observability but adds runtime overhead and operational complexity.

## 10. "How do you handle metadata read storms from sync-heavy users?"

### Why They Ask

They want assurance that metadata reads don't throttle the entire service during enterprise sync windows.

### Approach

- Layer per-region read replicas and delta-materialized views as suggested in [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/) so the metadata DB only serves aggregate cursors.
- Promote super-high-volume accounts to dedicated replica sets and pre-aggregate responses for clients before they request them.
- Trade-off: The precomputed deltas add slight staleness but keep tail latency under budget across millions of devices.

## 11. "How do you defend the upload path when bursts and large blobs arrive together?"

### Why They Ask

Uploads need to stay available even when rookies sync their entire photo libraries or third-party tools push multi-GB dumps.

### Approach

- Apply adaptive batching, partitioned queues, and burst controls from [03-hld-concepts/write-scaling](../../03-hld-concepts/write-scaling/), including write token buckets and deferred retries.
- Offload chunk uploads to the resumable session pipeline from [03-hld-concepts/large-blob-handling](../../03-hld-concepts/large-blob-handling/); metadata is written first while the bulky blob transfers asynchronously.
- Trade-off: Users may see slightly delayed finalization confirmation, but the system avoids cascading failures caused by unbounded parallel chunk storms.

## 12. "How do you manage long-running dedup/cleanup jobs without destabilizing user operations?"

### Why They Ask

Long-running jobs can end up contending with client activity if not carefully scheduled and tracked.

### Approach

- Model jobs using [03-hld-concepts/long-running-tasks](../../03-hld-concepts/long-running-tasks/) with unique IDs, heartbeat leases, visibility timeouts, and dead-letter queues.
- Integrate operators dashboards to observe job duration, retries, and failure rates; pause low-priority jobs during extreme client load.
- Trade-off: The tracking overhead is small compared to the cost of a runaway dedup job that exhausts the chunk store and throttles active uploads.
