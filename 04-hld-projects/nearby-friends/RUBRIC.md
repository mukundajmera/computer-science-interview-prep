# Nearby Friends - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| Requirements & Constraints | 15% | Explicitly calls out battery drain, NAT, and the need to limit fan-out to online friends only. |
| Capacity Estimation | 15% | Correctly identifies the egress/fan-out QPS multiplier ($14\text{M}/s$) as the critical system bottleneck. |
| Architecture & Protocols | 20% | Selects WebSockets for low overhead and centralized server state; avoids mobile P2P pitfalls. |
| Fan-out Mechanism | 20% | Uses Redis Pub/Sub (or similar lightweight memory bus) tailored to user-specific channels. |
| State Management | 15% | Separates ephemeral real-time state (Redis TTL) from persistent analytics (Cassandra/Kafka). |
| Edge Cases | 15% | Handles WebSocket reconnect storms, celebrity fan-out limits, and offline-to-online state hydration. |

## Performance bands

- **Strong Hire:** Quickly dismisses P2P, does the fan-out math accurately, designs a cleanly separated WebSocket/Pub/Sub architecture, and natively addresses the "offline friend comes online" state sync.
- **Hire:** Achieves the core WebSocket + Pub/Sub design but might need hints on separating the persistent storage path or managing the Redis cluster size.
- **Lean No Hire:** Struggles with the fan-out multiplier, attempts to use heavy HTTP polling, or tries to force a Geohash architecture that broadcasts to strangers.
- **No Hire:** Designs a mobile P2P system or fails to establish a working real-time connection model.

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [System Design](./DESIGN.md)