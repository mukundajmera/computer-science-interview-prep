# 📋 HLD Design: Nearby Friends

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: A "Nearby Friends" feature for a mobile app.
- Core user value: Users can see which of their friends are physically close to them (within 5 miles) in near real-time, along with their last active timestamp.

### Functional Requirements
- [x] FR1: View nearby friends within a 5-mile radius with distance and timestamp.
- [x] FR2: Mobile clients proactively send location updates every 30 seconds.
- [x] FR3: Inactive friends drop off the nearby list after 10 minutes (TTL).
- [x] FR4: Persist historical locations for analytics.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% for real-time feature |
| Read/Fan-out latency | $< 1\text{ s}$ end-to-end to online friends |
| Write throughput | $\approx 33,000\text{ updates/sec}$ |
| Fan-out throughput | $\approx 1.33\text{M pushes/sec}$ |
| Consistency | Eventual (loss of occasional packet acceptable) |

### Constraints
- Mobile constraints: Battery and data limits make P2P unviable.
- Fan-out constraint: Only fan out to currently *online* friends to save bandwidth and compute.

### Out of Scope
- Global geographic search (finding strangers nearby).
- Precise turn-by-turn navigation data.

---

## 2. 📊 Back-of-Envelope Estimation

### Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | $10\text{M}$ | input |
| Concurrent users | $1\text{M}$ | input |
| Ingest QPS | $33,333\text{ ops/s}$ | $1\text{M} / 30\text{ s}$ |
| Avg friends/user | $400$ | input |
| Online friends | $40$ | $400 \times 10\%$ active |
| Fan-out QPS | $1,333,333\text{ ops/s}$ | $33,333 \times 40$ |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| Redis Cache | $100\text{ B}$ | $1\text{M} \times 100\text{ B} \approx 100\text{ MB}$ (steady) | N/A |
| Historical DB | $50\text{ B}$ | $33,333 \times 86400 \times 50 \approx 144\text{ GB}$ | $\approx 52\text{ TB}$ |

### Decision Notes
- **Fan-out is the bottleneck:** $1.33\text{M}$ pushes/sec requires a robust distributed Pub/Sub mechanism.
- **Pub/Sub Cluster Size:** $1.33\text{M msgs/sec} / 100,000\text{ msgs/server} \approx 14\text{ Redis nodes}$.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: WebSocket for persistent, bidirectional communication (low overhead per message).

### Core Payloads
**Client -> Server (Location Update):**
```json
{
  "type": "location_update",
  "lat": 37.7749,
  "lng": -122.4194,
  "timestamp": 1629837482
}
```

**Server -> Client (Friend Update):**
```json
{
  "type": "friend_location",
  "friend_id": "uuid-1234",
  "lat": 37.7750,
  "lng": -122.4190,
  "timestamp": 1629837485
}
```

### Error Model
- Disconnects: Handled by client re-establishing the WebSocket connection.

---

## 4. 🗄️ Core Entities and Data Model

### Data Schemas

**1. Location History (Cassandra / S3)**
Used for write-heavy historical persistence.
```sql
CREATE TABLE location_history (
    user_id UUID,
    timestamp TIMESTAMP,
    latitude DOUBLE,
    longitude DOUBLE,
    PRIMARY KEY (user_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

**2. Redis Location Cache (Key-Value)**
Holds the latest location for online users with a TTL.
```text
Key: loc:{user_id}
Value: {lat: double, lng: double, ts: long}
TTL: 600s (10 minutes)
```

**3. Redis Pub/Sub Channels**
```text
Channel (User): channel:user:{user_id}
Channel (Geohash): channel:geohash:{geohash_id}
```
Friends subscribe to user channels, or the system can use Geohash channels for regional broadcast.

---

## 5. 🏗️ High-Level Architecture

### Component List
- **Load Balancer:** Routes WebSocket connections.
- **Netty/WebSocket Servers:** Maintain persistent, stateful connections with mobile clients.
- **Redis Pub/Sub Cluster:** Handles message routing between user channels.
- **Redis Location Cache:** Stores the last known location of users.
- **Location History Workers:** Asynchronously write to Cassandra or S3.

### Read Path (User comes online)
1. Client connects via WebSocket to a Netty/WebSocket server.
2. Server fetches user's friend list from a Friend Graph Service.
3. Server queries Redis Location Cache for the latest locations of those friends.
4. Server filters friends $> 5$ miles away and sends the initial list to the client.
5. Server subscribes the client\'s WebSocket connection to the Pub/Sub channels of all friends (`channel:user:{friend_id}`) or relevant Geohash channels.

### Write Path (Location Update)
1. Client sends a location update over WebSocket.
2. Netty/WebSocket server receives it and writes to the Redis Location Cache (`loc:{user_id}`) with a 10m TTL.
3. Netty/WebSocket server publishes the update to the user\'s Pub/Sub channel (`channel:user:{user_id}`) or their current Geohash channel.
4. Redis Pub/Sub pushes the message to all subscriber WebSocket servers.
5. Subscriber servers calculate the distance; if within 5 miles, forward it to the connected friends' clients.
6. A copy of the event is dropped onto a Kafka topic for background workers to write to Cassandra or S3.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Peer-to-Peer vs Centralized WebSocket + Pub/Sub
- **Bottleneck:** Mobile constraints (battery, data, NAT).
- **Chosen pattern:** Centralized stateful Netty/WebSocket servers + Redis Pub/Sub.
- **Alternative considered:** P2P connection between phones.
- **Trade-off accepted:** P2P drains battery rapidly by keeping antennas awake and requires constant polling. Centralized WebSockets batch data efficiently and shift the heavy fan-out work to the cloud.

### Deep Dive B: Bounding Fan-out (User vs Geohash Channels)
- **Bottleneck:** Global "celebrity" fan-out.
- **Chosen pattern:** Channel per user (`channel:user_id`) or per Geohash tile depending on density. Typically only friends subscribe.
- **Alternative considered:** Geohash grid channels (subscribing to a physical area).
- **Trade-off accepted:** Since the feature is strictly "nearby *friends*", subscribing to friends' channels tightly bounds the fan-out to $O(\text{online friends})$. Geohash channels would receive updates from strangers, wasting client bandwidth and server processing.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Communication | WebSockets | Polling / SSE | Bidirectional, low overhead per msg | Need simple one-way push |
| Fan-out | Redis Pub/Sub | Kafka | Lower latency, ephemeral, high channel count | Need message replay |
| History DB | Cassandra | PostgreSQL | Massive write throughput | Analytics needs complex joins |

---

## 8. 🔮 Follow-up Questions

1. How do you handle a Redis Pub/Sub node crashing?
2. What happens if a user has 10,000 friends (celebrity problem)?
3. How can we use Geohashes to extend this to finding random strangers nearby?

---

## 9. 🧩 Variants and Extensions

- **Variant 1 (Discover Strangers):** Transition from user-centric channels to Geohash grid channels.
- **Variant 2 (Battery Saver):** Dynamically adjust the 30-second update interval based on user speed (accelerometer data) or remaining battery life.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I did not assume P2P works well on mobile.
- [x] I correctly identified the fan-out (1.33M/s) as the primary bottleneck, not ingest.
- [x] I separated the ephemeral real-time cache (Redis) from the persistent history (Cassandra).
- [x] I used channels based on user IDs, not geohashes, as it's specifically for *friends*.

---
**Real-world reference**: See how Uber solved this in the [Uber case study](../../case-studies/uber-realtime/)
