# File Storage — Common Interview Pitfalls

## 1. Treating Upload as Single HTTP Request

Large files need resumable chunk/multipart flows; otherwise retries are expensive and failure-prone.

## 2. No Explicit Upload Session Model

Without session metadata, clients cannot recover after network interruption.

## 3. Missing Checksum Validation

Per-chunk and final-file validation are required to catch corruption.

## 4. Ignoring Sync Cursor Semantics

Polling without cursors causes missed updates and duplicate event handling.

## 5. Weak Conflict Story

Last-write-wins alone can silently discard user work.

## 6. Conflating Metadata and Content Consistency

Metadata often needs stronger guarantees than blob transfer completion.

## 7. No Cost Strategy at Scale

PB-scale systems need dedup/tiering considerations even if treated as follow-up.

## 8. No Access-Control Boundary in Share Links

Share links without revocation/expiry controls become long-term security risk.

---

## Quick Self-Check

- Did I define chunk upload lifecycle clearly?
- Did I include sync cursor and conflict behavior?
- Did I discuss metadata vs content consistency choices?
- Did I mention integrity and durability controls?

---

## 8. Choosing the Wrong Realtime Transport by Default

### ❌ The Mistake

Using one channel for all realtime scenarios (usually WebSocket) without validating whether communication is one-way, bidirectional, bursty, or mostly idle.

### 🎯 What the Interviewer Expects

- A transport decision matrix tied to product behavior and cost profile.
- Explicit fallback strategy and reconnect replay semantics.
- Ordering scope and deduplication plan for multi-device users.

### 💡 Tip

State channel selection as a requirement-driven decision, not a technology preference.

## 9. Over- or Under-Coordinating Contention Paths

### ❌ The Mistake

Either adding distributed locks too early or ignoring conflicts until oversell/double-assignment incidents appear.

### 🎯 What the Interviewer Expects

- An escalation ladder: optimistic -> pessimistic/serialized -> distributed coordination.
- Measurable triggers (conflict rate, retry depth, lock wait time).
- Idempotent retries, bounded backoff, and failure-mode handling.

### 💡 Tip

Show how you would isolate hot keys rather than globally locking the entire workload.

## 10. Missing Durable Workflow Boundaries for Multi-step Operations

### ❌ The Mistake

Treating multi-service flows as a single best-effort request chain without durable checkpoints, compensation, or idempotency.

### 🎯 What the Interviewer Expects

- Explicit step state machine and compensation strategy.
- Durable checkpointing and resume path after crash/redeploy.
- Idempotency requirements for every side-effecting step.
- Versioning plan for in-flight workflow upgrades.

### 💡 Tip

If a flow can partially succeed, describe how it recovers before describing happy-path latency.

## 11. Not scaling metadata reads for sync storms

### ❌ The Mistake

Assuming metadata reads stay light during enterprise sync windows. When thousands of devices poll for deltas, the read path becomes the bottleneck.

### 🎯 What the Interviewer Expects

- Reference [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/) and describe per-region read replicas, materialized delta tables, and cached sync cursors so the metadata store never sees the full surge.
- Include tooling to promote hot users to dedicated replica sets and to fall back to a pre-aggregated delta if the primary read tier saturates.

### 💡 Tip

Highlight the trade-off between freshness and availability: rounding sync cursors to the nearest second reduces load while staying within acceptable staleness for enterprise clients.

## 12. Letting write bursts and blobs overwhelm the upload path

### ❌ The Mistake

Sending every large file or bursty enterprise sync directly through the metadata+chunk pipelines without adaptive batching or throttling.

### 🎯 What the Interviewer Expects

- Explain how [03-hld-concepts/write-scaling](../../03-hld-concepts/write-scaling/) gives you partitioned write lanes, batching windows, and per-tenant rate limits so the upload service can absorb 10x peak traffic.
- Call out chunked upload controls from [03-hld-concepts/large-blob-handling](../../03-hld-concepts/large-blob-handling/), like resumable sessions, per-chunk checksums, and storage tiering, so a 10 GB file never stalls the pipeline.
- Surface progress tokens, abort/resume hooks, and graceful failure for clients when the write path is overloaded.

### 💡 Tip

Leveraging durable session tracking lets you shed load without losing user intent — you can accept the upload (and chunk meta) before the actual blob is ready.

## 13. Ignoring long-running background tasks

### ❌ The Mistake

Treating dedup, trash cleanup, or malware scanning as fire-and-forget scripts with no monitoring or retries.

### 🎯 What the Interviewer Expects

- Use job-tracking patterns from [03-hld-concepts/long-running-tasks](../../03-hld-concepts/long-running-tasks/) so each cleanup job carries an idempotency key, heartbeat, and dead-letter policy.
- Surface dashboards for stuck jobs and integrate alerts so the ops team can respond before sync sessions fail.
- Tie it back to user SLAs: a runaway garbage collection job can suddenly consume the chunk store and throttle active uploads if left unchecked.

### 💡 Tip

When you describe job health metrics, mention how you reconcile long-running tasks with quota-based operations (e.g., pause dedup jobs during high tenant traffic).
