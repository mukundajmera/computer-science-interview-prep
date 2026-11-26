# Nearby Friends

## Problem Statement
Design a "Nearby Friends" feature for a mobile app (similar to Facebook's Nearby Friends or Snapchat's Snap Map). The system allows users to see which of their friends are physically close to them and when they were last active.

---

## Requirements and constraints

### Functional requirements
1. View nearby friends within a 5-mile radius, including distance and timestamp.
2. Mobile clients proactively send location updates every 30 seconds.
3. Inactive friends drop off after 10 minutes (TTL).
4. Persist historical locations for analytics and retroactive tracing.
5. Privacy controls allowing users to opt-in or opt-out of sharing their location.

### Non-functional requirements

| Requirement | Target |
|---|---|
| Efficiency | Minimize mobile battery drain and network data consumption (persistent WebSockets preferred) |
| Availability | 99.99% for core functionality |
| Delivery latency | $< 1\text{ s}$ end-to-end fan-out to online friends |
| Throughput (Ingest) | $\approx 33,000\text{ inbound updates/sec}$ |
| Throughput (Fan-out)| $\approx 1.33\text{M location pushes/sec}$ |
| Consistency | Eventual consistency; loss-tolerant to occasional dropped packets |
| Scale | $10\text{M}$ DAU, $10\%$ active at any time ($1\text{M}$ concurrent users) |

### Constraints
- Mobile battery and data consumption are significant constraints.
- Real-time updates only fan out to *online* friends; offline friends pull the latest state when they come online.

### Out of scope
- Global geographic search (finding strangers nearby).
- Precise turn-by-turn navigation data.
- User management and friend graph setup (assume existing services for these).

## Key design challenges
1. P2P is unviable on mobile due to battery, firewalls, and NAT. Centralized fan-out via WebSocket and Pub/Sub is required.
2. Handling the massive fan-out of $1.33\text{M}$ pushes/sec reliably and cost-effectively.
3. Bounding the fan-out to prevent "celebrity" issues, utilizing user-centric channels rather than global geohash channels for this specific feature.

## Related links
- [HLD Design Template](../DESIGN-TEMPLATE.md)
- [WebSockets](../../03-hld-concepts/websockets/THEORY.md)
