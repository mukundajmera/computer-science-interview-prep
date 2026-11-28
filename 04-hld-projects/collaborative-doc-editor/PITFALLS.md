# Collaborative Document Editor — Common Interview Pitfalls

## 1. Treating Realtime Delivery as Consistency
Low-latency delivery does not guarantee convergence under concurrent edits.

## 2. No Operation Versioning
Without base version/op IDs, server cannot safely transform or reject stale edits.

## 3. Single Node Session Assumption
A single websocket node becomes a bottleneck and availability risk.

## 4. Missing Replay-on-Reconnect
Clients reconnecting without replay drift from canonical state.

## 5. Snapshot-Free Infinite Logs
No compaction leads to expensive recovery and unbounded replay cost.

## 6. Coupling Metadata CRUD with Edit Hot Path
Metadata traffic can disrupt edit latency if paths are not isolated.

## 7. Ignoring Presence Semantics
Cursor/presence staleness degrades UX and creates phantom collaborators.

## 8. Assuming Document-ID Consistent Hashing Solves Hot-Document Bottlenecks
Pinning a viral document to one Collaboration Engine node via consistent hashing still overwhelms that node's CPU and fan-out bandwidth during intense bursts (20 ops/sec across 50+ or thousands of viewers). Isolate high-fanout broadcasts by adding an aggregation tier or switching reader-only overflow viewers to CDN-backed polling or HLS.

## 9. Underestimating WebSocket Gateway Memory and Dead-Connection Leaks
Sizing gateway RAM only for the 10 KB application payload ignores ~30 KB of kernel TCP/TLS socket buffers per connection, causing OOM crashes well before 10M concurrent sockets. Account for full per-socket overhead (~40 KB total) and enforce WebSocket Ping/Pong heartbeats that terminate half-open sockets and emit `presence_leave`.

## 10. Using Naive Local Undo That Reverts Other Users' Concurrent Edits
Restoring a client's prior document snapshot on Undo silently wipes out edits other collaborators made after the original action. Store per-user inverse operations in the undo buffer and transform or merge them through the OT/CRDT engine against all subsequent operations.

## 11. Building an N^2 Peer Mesh Between Gateways and Collaboration Nodes
Maintaining direct mesh connections between every WebSocket Connection Gateway and every Collaboration Engine node breaks down as fleets scale and churn. Decouple fan-out through a Redis Pub/Sub broker keyed by `documentId` and fall back to periodic Cassandra polling if Pub/Sub partitions.

## 12. Treating CRDT Library Names as a Complete Concurrency Design
Naming Yjs or Automerge without defining deterministic tie-breaking, unique `(client_id, clock)` operation IDs, or offline state-vector sync leaves duplicate-retry and divergence bugs unresolved. Specify deterministic ordering rules for concurrent same-origin inserts and use unique CRDT IDs so retried edits after a gateway crash remain idempotent.

---

## Quick Self-Check

- Did I define operation IDs, base version, and replay behavior?
- Did I provide a bounded recovery path (log + snapshots)?
- Did I describe how document sessions scale horizontally?
- Did I explain how to mitigate hot-document bottlenecks beyond basic consistent hashing?
- Did I size WebSocket gateway RAM including kernel TCP/TLS overhead and heartbeat cleanup?
- Did I handle collaborative undo/redo via transformed inverse operations rather than raw snapshots?
- Did I decouple gateway fan-out with Redis Pub/Sub instead of an N^2 mesh?
- Did I specify deterministic CRDT tie-breaking, idempotent op IDs, and offline state-vector sync?
