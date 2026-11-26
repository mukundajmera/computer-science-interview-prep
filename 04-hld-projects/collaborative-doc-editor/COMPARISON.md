# Collaborative Document Editor — Comparison

## Collaborative Editor vs Chat Service

| Concern | Collaborative Editor | Chat Service |
|---|---|---|
| Ordering scope | Per-document operation stream | Per-conversation message stream |
| Merge semantics | Concurrent transform/rebase | Append-dominant ordering |
| Recovery unit | Snapshot + operation replay | Message log replay |

## Collaborative Editor vs Ride Sharing

| Concern | Collaborative Editor | Ride Sharing |
|---|---|---|
| Core realtime data | Text operations and presence | Driver locations and trip state |
| Consistency target | Eventual convergence | Strong assignment correctness |
| Session affinity | Document ID | Geo zone / trip ID |

## Collaborative Editor vs Distributed Cache

| Concern | Collaborative Editor | Distributed Cache |
|---|---|---|
| Hot key pattern | Popular documents | Popular cache keys |
| Replay need | Required for reconnect consistency | Mostly not required for read path |
| State model | Operation log + snapshots | Key-value with TTL/eviction |
