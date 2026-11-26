# Stock Exchange Matching Engine - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
|---|---|---|
| Domain Understanding | 20% | Correctly identifies price-time priority, limit vs market orders, and the need for L2 data. |
| Latency Optimization | 30% | Removes DB from critical path. Proposes single-threaded, in-memory matching. Mentions GC tuning, object pooling, or ring buffers. |
| High Availability | 25% | Uses a Sequencer/Event Sourcing pattern for deterministic active-standby failover instead of standard DB replication. |
| Data Structures | 15% | Uses optimal structures (`TreeMap` / `DoublyLinkedList` / `HashMap`) to achieve $O(1)$ matching and $O(1)$ cancellation. |
| System Communication | 10% | Understands UDP multicast for market data and reliable TCP/reliable messaging for execution reports. |

## Performance bands

- **Strong Hire:** Candidate immediately recognizes this is not a CRUD application. Designs an in-memory sequencer-based architecture. Optimizes data structures for $O(1)$ access where required. Articulates how determinism solves the HA problem.
- **Hire:** Keeps the DB out of the critical path. Uses caching effectively. Understands price-time priority. May need minor hints on how to handle exact failover synchronization without distributed locks.
- **No Hire:** Attempts to build the matching engine using Postgres transactions or Redis locks. Relies on horizontal scaling of a single order book, leading to race conditions. Unaware of the latency implications of network hops during matching.

## Cross-links
- [Problem](./PROBLEM.md)
- [Design](./DESIGN.md)
