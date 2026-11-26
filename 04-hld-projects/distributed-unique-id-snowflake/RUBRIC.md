# Distributed Unique ID Generator (Snowflake) — Interview Scoring Rubric

Use this rubric to evaluate design quality and implementation thinking consistently for the Snowflake ID generator project.

> Related: [PROBLEM](./PROBLEM.md) · [APPROACH](./APPROACH.md) · [DESIGN](./DESIGN.md)

---

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Identifies strict 64-bit size constraint, numerical sorting necessity, and high throughput needs. |
| Domain model quality | 25% | Clean logical separation of timestamp, worker ID, and sequence components within the 64-bit integer. |
| Worker Coordination | 25% | Robust understanding of how to assign unique Worker IDs using a CP system like ZooKeeper to avoid collisions. |
| Failure & Clock Drift | 20% | Explicit strategy for NTP backward clock shifts (e.g., wait vs fail-fast) and sequence exhaustion. |
| Extensibility & Trade-offs| 15% | Discusses custom epoch lifespan limits, handling integer precision in JavaScript clients, and latency vs consistency trade-offs during clock drift. |

## Performance bands

- `1/5`: Proposes UUIDv4 without realizing index fragmentation, or central database auto-increment without addressing scaling bottlenecks. Ignores clock drift entirely.
- `3/5`: Mentions the Snowflake bit layout and worker ID concept, but lacks a concrete mechanism for assigning worker IDs or mishandles the JavaScript 53-bit precision issue.
- `5/5`: Clear architecture using ZooKeeper for dynamic worker lease assignment, strict clock backward shift logic, and clear trade-off articulation between availability and collision-freedom.

## Cross-links

- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
