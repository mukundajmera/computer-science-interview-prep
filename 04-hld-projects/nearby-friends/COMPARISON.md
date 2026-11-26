# Nearby Friends - Comparison

## Fan-out Strategies

| Concern | User-centric Channels (Chosen) | Geohash Grid Channels |
|---|---|---|
| **Concept** | Subscribe to `channel:{friend_id}` | Subscribe to `channel:{geohash_grid}` |
| **Best For** | Social graph constrained features ("Nearby Friends") | Global proximity features ("Find a driver/stranger") |
| **Client Bandwidth** | Low (Receives updates only for friends) | High (Receives updates for *everyone* in the grid) |
| **Server Filtering** | Distance calculated on server; unneeded pushes dropped | Client must filter out non-friends |
| **Edge Cases** | Celebrities (thousands of friends) cause high localized fan-out | Dense cities (thousands of people in one grid) cause high grid fan-out |

## Real-time Transport Options

| Feature | WebSockets (Chosen) | Long Polling | Server-Sent Events (SSE) |
|---|---|---|---|
| **Communication** | Full-duplex (Bidirectional) | Half-duplex (Client requests, server holds) | Simplex (Server to Client only) |
| **Overhead** | Very low (after initial handshake) | High (HTTP headers sent on every request/reconnect) | Low (but client still needs separate HTTP POST for writes) |
| **Suitability** | Ideal. Client sends updates, server pushes fan-out. | Poor. Will drain battery fast with 30s updates. | Okay, but requires parallel HTTP request path for ingest. |

## Messaging Bus (Pub/Sub)

| Characteristic | Redis Pub/Sub (Chosen) | Apache Kafka |
|---|---|---|
| **Persistence** | None (Fire and forget) | High (Durable commit log) |
| **Latency** | Sub-millisecond | Low, but higher than Redis due to disk I/O |
| **Channel Count** | Millions (very lightweight) | Tens of thousands (partition limits) |
| **Replayability** | No | Yes |
| **Decision** | **Winner:** Ephemeral location data doesn't need replay for real-time. We need massive channel counts for user-level routing. | **Loser:** Overkill for transient state; channel per user is unviable. |

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design](./DESIGN.md)