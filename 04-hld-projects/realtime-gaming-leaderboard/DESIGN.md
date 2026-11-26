# Real-Time Gaming Leaderboard - High-Level Design

## 1. 📝 Requirements and Constraints

### Problem Statement
- **System to design:** A real-time leaderboard for a competitive gaming platform.
- **Core user value:** Players need instantaneous feedback on their rank and performance relative to millions of other players to maintain engagement.

### Functional Requirements
- [x] **FR1:** Increment player score upon match win.
- [x] **FR2:** Real-time Global Top 10 (or Top 100) players retrieval.
- [x] **FR3:** Return a specific player's exact global rank.
- [x] **FR4:** Return a relative rank window (e.g., 4 ranks above and below the player).
- [x] **FR5:** Support monthly tournament lifecycles (active play and historical archival).

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Read latency | < 50ms P99 |
| Write latency | < 50ms P99 |
| Throughput (Writes) | 500 avg QPS, 2,500 peak QPS |
| Consistency | Strong consistency on the read-your-own-writes path for rank updates |
| Durability | Persistent disaster recovery from a durable store |

### Constraints
- Tie-breakers: Earlier timestamp wins if scores are identical.
- Memory: In-memory datasets must be optimized.

---

## 2. 📊 Back-of-Envelope Estimation

### Traffic
| Metric | Value | Formula |
|---|---|---|
| DAU | 5,000,000 | given |
| Matches/user/day | ~10 | assumed average |
| Daily updates | 50,000,000 | DAU × matches |
| Avg QPS | ~578 | daily / 86400 |
| Peak QPS | ~2,500 | avg × burst factor (~4.5x) |

### Storage (RAM for Redis)
*Note: A Redis ZSET element consists of a dictEntry (24 bytes), zskiplistNode (avg ~48 bytes), robj string wrapper (16 bytes), string payload (16-36 bytes), and jemalloc padding, totaling ~200-250 bytes per member.*

| Data Type | Avg Size | Total Volume | Memory Overhead |
|---|---|---|---|
| Active Tournament Users | 25M MAU | 25M users | ~5.0 - 6.2 GB |
| At Extreme Scale | 500M users | 500M users | ~100 - 125 GB |

### Decision Notes
- **Memory forces architecture:** At 25M users, the dataset requires ~5.0 - 6.2 GB, which fits on a standard Redis node. At 500M users, it requires roughly 100 - 125 GB, which is manageable on a large instance, but the 250k QPS limit will force sharding strategies.
- **Durability requirement:** Because Redis is in-memory, we must back it with an asynchronous durable write path to MySQL.

---

## 3. 🔌 API / System Interface

### External Contract
- **Protocol choice:** REST (HTTP) for simple integration with game clients and web portals.

### Core Endpoints

```http
POST /api/v1/tournaments/{tournament_id}/scores
{
  "user_id": "u_12345",
  "points": 10,
  "timestamp": 1698765432100
}
```
*Response: Returns the new total score and the updated exact rank.*

```http
GET /api/v1/tournaments/{tournament_id}/leaderboard/top?limit=10
```
*Response: Returns the top 10 users in the tournament.*

```http
GET /api/v1/tournaments/{tournament_id}/users/{user_id}/rank?relative_window=4
```
*Response: Returns the user's exact rank and the 4 players above and below them.*

---

## 4. 🗄️ Core Entities and Data Model

### Data Schemas

**MySQL Source of Truth & Leaderboard Rebuild Store**
```sql
CREATE TABLE user_tournament_score (
    tournament_id VARCHAR(32) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    score BIGINT NOT NULL DEFAULT 0,
    last_win_timestamp BIGINT NOT NULL,
    PRIMARY KEY (tournament_id, user_id),
    INDEX idx_score (score DESC)
);
```

**Redis Data Structure**
- **Key:** `leaderboard:{tournament_id}`
- **Type:** Sorted Set (`ZSET`)
- **Member:** `user_id`
- **Score Formulation:** To handle tie-breakers (earlier timestamp wins), we must adapt Redis's default behavior, which sorts identical scores lexicographically by member ID. We use a composite score:
  `composite_score = score + (1.0 - (timestamp % 86400) / 86400.0)`
  *Note: Redis scores are 64-bit floating point numbers. We store the integer score in the whole number portion and subtract the daily fractional time from 1.0, appending it as the decimal. Alternatively, we could use a two-tier structure mapping `score` to a secondary structure, but a composite float is faster.*

### Key Access Patterns
1. **Write path mutation:** `ZINCRBY` (actually, we read the old score, calculate the new composite score based on the new timestamp, and use `ZADD` to overwrite, since `ZINCRBY` cannot easily handle the fractional timestamp math dynamically).
2. **Read path (Top N):** `ZREVRANGE leaderboard:{id} 0 9 WITHSCORES`
3. **Read path (Relative rank):** 
   - `rank = ZREVRANK leaderboard:{id} {user_id}`
   - `ZREVRANGE leaderboard:{id} (rank - 4) (rank + 4)`

---

## 5. 🏗️ High-Level Architecture

![Architecture Diagram](diagrams/architecture.mmd)

### Component List
- **API Gateway:** Routes requests and handles auth/rate-limiting.
- **Score Service:** Handles write paths, calculates composite scores, updates Redis, and publishes events.
- **Rank Lookup Service:** Handles read queries directly against Redis.
- **Event Stream (Kafka):** Ensures durable, ordered messaging for score updates.
- **DB Persist Worker:** Consumes Kafka events and batches updates to MySQL.

### Read Path
1. Client requests top 10 or relative rank.
2. Request routed to **Rank Lookup Service**.
3. Service executes `ZREVRANK` and `ZREVRANGE` on the **Redis Replica** (to distribute read load).
4. Returns formatted response < 50ms.

### Write Path
1. Client wins match, posts score increment to **Score Service**.
2. Service calculates the new composite score (score + inverted timestamp).
3. Service synchronously updates **Redis Primary** (`ZADD`).
4. Service asynchronously drops a message onto **Kafka**.
5. Client receives HTTP 200 OK.
6. In the background, **DB Persist Worker** batches Kafka messages and upserts into **MySQL**.

### Failure-aware Path
- **Redis Crash:** If Redis crashes, a new instance is spun up and rebuilt using a background script reading from the MySQL `user_tournament_score` table.
- **Kafka Unavailability:** The Score Service buffers locally or returns a 500 to the client, forcing the client to retry.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Tie-breaker Implementation in Redis
- **Bottleneck:** Redis natively only sorts by the numeric score. If scores are equal, it sorts lexicographically by the string member (`user_id`), which ignores the "first to achieve score wins" requirement.
- **Chosen pattern:** Composite score using the 64-bit float precision. 
  By calculating the fractional time within a 24-hour window `(timestamp % 86400) / 86400.0` and subtracting it from 1.0 (to invert it so earlier times yield a higher fractional component), we append it to the integer score.
- **Trade-off accepted:** Float precision limits. An IEEE 754 64-bit float has 53 bits of precision (safe integers up to 9,007,199,254,740,992, or ~9*10^15). Care must be taken that the integer score does not consume so many bits that it crushes the fractional timestamp precision, otherwise ties might be evaluated incorrectly. An alternative to avoid float precision limits is a two-tier Redis hash mapping (a ZSET of scores pointing to secondary lists ordered by timestamp), but it requires multiple round-trips or Lua scripts.

### Deep Dive B: Extreme Scale Sharding (500M Users / 250k QPS)
- **Bottleneck:** A single Redis node maxes out at ~100k ops/sec and 500M users require 100 - 125 GB of memory.
- **Chosen pattern:** Score-range sharding.
  We divide the leaderboard into score buckets (e.g., Shard A: 1M-infinity, Shard B: 100k-999k, Shard C: 0-99k).
  To find a user's absolute rank:
  1. Locate the user's shard (requires a secondary hash table of `user_id` -> `score`).
  2. Compute rank inside the specific shard.
  3. Add the total `ZCARD` (count) of all shards representing higher score ranges.
- **Alternative considered:** Hash sharding by `user_id`. Rejected because calculating the global top 10 would require querying all nodes and aggregating, and calculating absolute rank becomes $O(N \text{ shards})$.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Primary Data Store | Redis Sorted Set | RDBMS (MySQL) | $O(\log N)$ rank calculation vs $O(N)$ full table scans. | Scale forces cluster cost |
| Persistence Strategy | Async via Kafka to MySQL | Sync write to MySQL | Real-time gaming requires < 50ms latency; sync DB writes introduce too much latency jitter. | Need strong global consistency |
| Scaling Strategy | Score-Range Sharding | Hash Sharding | Score-range allows fast global Top N and absolute rank queries. | Extreme single bucket hotspot |

---

## 8. 🔗 Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach & Sizing](APPROACH.md)
- [Rubric](RUBRIC.md)
- [Follow-ups](FOLLOW-UPS.md)
- [Comparison](COMPARISON.md)
- [Strong Answer](STRONG-ANSWER.md)
- [Pitfalls](PITFALLS.md)

---
**Real-world reference**: See how Uber solved this in the [Uber case study](../../case-studies/uber-realtime/)
