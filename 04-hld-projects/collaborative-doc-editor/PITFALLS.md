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

---

## Quick Self-Check

- Did I define operation IDs, base version, and replay behavior?
- Did I provide a bounded recovery path (log + snapshots)?
- Did I describe how document sessions scale horizontally?
