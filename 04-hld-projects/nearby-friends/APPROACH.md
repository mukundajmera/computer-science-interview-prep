# Design Approach for Nearby Friends

## Interview flow (45 minutes)

| Phase | Time | Focus |
|---|---|---|
| Clarify requirements | 5 min | Distance radius, update frequency, online vs offline behavior |
| Capacity estimation | 7 min | Concurrent users, fan-out multiplier, ingest and egress QPS |
| API + data model | 10 min | WebSocket payload schema, Redis location cache schema, Cassandra history schema |
| Architecture | 15 min | WebSocket connection management, Redis Pub/Sub fan-out, worker nodes |
| Deep dives | 5 min | Handling offline users coming online, scaling Redis Pub/Sub |
| Wrap-up | 3 min | Bottlenecks, P2P alternative constraints, Geohash extension |

## Suggested execution order
1. Establish the "online-only fan-out" core assumption to bound the problem.
2. Run the math explicitly to show why fan-out (14M/s) is the primary bottleneck over ingest (334k/s).
3. Design the stateless WebSocket handler layer mapping users to connections.
4. Introduce Redis Pub/Sub per user channel to solve the fan-out efficiently.
5. Add the persistent location history sink using Cassandra or a stream pipeline.
6. Discuss failure modes (Redis node crash, WebSocket server disconnect).