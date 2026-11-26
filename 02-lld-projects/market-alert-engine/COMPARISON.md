# Market Alert Engine - Comparison

## Architectural Approaches

| Concern | Synchronous Evaluation | Asynchronous Stream Processing |
|---|---|---|
| **Latency** | Lowest latency. Ticks evaluated inline. | Higher latency due to queueing and batching. |
| **Throughput** | Limited by single-thread CPU or blocking locks. | High throughput. Can fan out workers. |
| **State Management** | In-memory locks. Simple but unscalable. | Distributed caches (Redis) or local state with partitioning. |
| **Fault Tolerance** | Rules and state lost on crash. | State recovery via event sourcing or snapshotting. |

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)
