# Search Autocomplete - High-Level Design

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: Search Autocomplete
- Core user value: Return top-5 suggestions matching a user's prefix in real-time to reduce typing effort.

### Functional Requirements
- [x] FR1: Return top-5 suggestions matching prefix in real time as the user types.
- [x] FR2: Rank suggestions by historical query frequency/popularity.
- [x] FR3: Case-insensitive matching (lowercase English characters `[a-z]`).
- [x] FR4: Blacklist/profanity filter to drop inappropriate suggestions.
- [x] FR5: Offline aggregation pipeline to recompute frequencies and rebuild Trie.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% (stale suggestions preferred over outages) |
| Read latency | < 100 ms P99 end-to-end |
| Write latency | Async (append-only logging) |
| Throughput | 48,000 peak QPS |
| Consistency | Eventual (Trie rebuilt periodically) |
| Durability | High (analytics logs stored reliably) |

### Constraints
- Regulatory/compliance: Standard data privacy for queries.
- Budget/cost preference: High RAM usage allowed for low latency.
- Team/operational constraints: Manageable batch pipeline operations.
- Region/geography constraints: CDN and multi-region deployment.

### Out of Scope
- Spell check and auto-correction.
- Personalization based on user history.

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | 10M | input |
| Requests/user/day | 40 (10 searches × 4 keystrokes avg) | input |
| Daily requests | 400M | DAU × requests/user |
| Avg QPS | ~4,630 | daily / 86400 |
| Peak QPS | ~48,000 | avg × 10 (burst factor) |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| New Queries | 20 bytes | 0.4 GB | 146 GB |

### Decision Notes
- Which estimate forces a design choice? 48,000 Peak QPS and < 100 ms latency force caching at the node level in the Trie and returning results from RAM.
- What assumption is most uncertain? The exact distribution of search term popularity (Zipf's law distribution) affecting cache hit rates.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: REST
- Auth model: API Key / User Token for rate limiting
- Rate limiting policy: 100 requests per minute per user/IP.

### Core Endpoints
```http
GET /api/v1/search/autocomplete?q={prefix}
```
**Response:**
```json
{
  "prefix": "tw",
  "suggestions": ["twitter", "twitch", "twilight", "twins", "twister"]
}
```

### Error Model
- `400` invalid input (e.g., prefix too long)
- `429` throttled (rate limited)
- `5xx` internal dependency failure

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- Entity A: Query Analytics Log
- Entity B: Query Frequency
- Entity C: Trie Cache Data

### Storage Choices
- Primary DB: Relational or NoSQL (e.g., Cassandra) for `query_frequency` (reason: large scale analytics aggregation).
- Cache: Redis (reason: low latency KV store for prefix -> top-5 mapping).
- Search index: Custom Trie Server (reason: efficient memory structure for prefix matching).
- Blob/object storage: S3/GCS (reason: raw analytics log cold storage).

### Key Access Patterns
1. Read path query: Look up prefix in Cache/Trie for top-5 suggestions (O(1)).
2. Write path mutation: Append query execution to Kafka log.
3. Secondary lookup: Batch job reading full logs to aggregate frequencies.

### Partition and Index Notes
- Partition key: Prefix for caching; Query text for frequency DB.
- Hot key risk: Common prefixes (e.g., "a", "th") can cause hot keys. Mitigated by CDN and edge caching.
- Required indexes: `query_text` in analytics DB for efficient grouping.

---

## 5. 🏗️ High-Level Architecture

**Refer to:** `diagrams/architecture.mmd`

### Component List
- API Gateway
- Query Service (Stateless app tier)
- Distributed Trie Cache (Redis)
- Trie Server cluster
- Async pipeline: Analytics Log -> Kafka -> Flink/Spark Streaming Aggregator -> Database -> Trie Builder
- Observability and control plane

### Read Path
1. Client sends keystroke `GET /api/v1/search/autocomplete?q=prefix`.
2. Request hits CDN, then API Gateway and is routed to Query Service.
3. Query Service queries Distributed Trie Cache (Redis). If cache miss, Service queries the Trie Server cluster, updates cache, and returns to client.

### Write (Aggregation) Path
1. User executes a search query.
2. Query execution appended to Analytics Log.
3. Log ingested into Kafka.
4. Flink/Spark Streaming Aggregator processes the data and updates the Database.
5. Trie Builder fetches from Database to rebuild/update Trie Server cluster.

### Failure-aware Path
- Dependency timeout behavior: Fast timeout on Trie/Cache (e.g., 50ms) to ensure overall <100ms.
- Retry policy + idempotency: Clients retry on 5xx, but with exponential backoff. Read path is idempotent.
- Degraded mode: Return empty suggestions or local browser cache rather than blocking the UI.

---

## 6. 🔍 Deep Dives (Pick 1-2)

### Deep Dive A: Trie Optimization & Sharding Strategy
- Bottleneck: Standard Trie traversal O(p + m log k) is too slow at ~120k peak QPS. Trie size (~100GB) exceeds single machine limits.
- Chosen pattern: Node-level Top-k Caching to lower read latency to O(p).
- Sharding pattern: Alphabetical partition vs Consistent hashing on prefix hash. Consistent hashing on a shard key (e.g., first 1-2 characters or hash of prefix) distributes the load better, avoiding hotspots on popular letters like 'a' or 's'.
- Trade-off accepted: Increased memory footprint (caching top-5 at each node) for dramatically lower read latency.

### Deep Dive B: Data Schema for Frequency Updates
- Schema consideration: SQL/NoSQL schemas for query frequency table and historical trends.
- Query frequency table needs quick updates and aggregation capabilities. Example schema: `(query_string, frequency_count)`.
- Historical trends could be stored with time-based partitions (e.g., hourly/daily rollups) to support decay and trend discovery.
- Consistency model: Eventual consistency via Flink/Spark Streaming pipeline.
- Failure handling: If the batch/streaming job fails, the current Trie continues serving (stale data is acceptable for availability).

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Trie Update | Offline Batch | Real-time Synchronous | Lock contention on real-time updates breaks latency constraints. | Demand for minute-level trending topics. |
| Suggestion Lookup | Node-level Top-k Caching | Dynamic Subtree Traversal | Lowers lookup to O(p). | If Trie size exceeds memory capacity constraints. |
| Client Requests | Debouncing (50ms) | Request per keystroke | Reduces unnecessary server load by 20-30%. | Changes in network latency/client behavior. |

---

## 8. 🔮 Follow-up Questions

1. What changes at 10x scale?
   - Introduce prefix-based sharding for the Trie Server and Redis cluster to handle memory and traffic limits.
2. What fails first under a regional outage?
   - The serving layer (Autocomplete Service/Cache). Multi-region active-active deployment is required for high availability.
3. How does the design change for strict consistency?
   - Requires real-time updates with distributed locks, heavily degrading latency (not recommended for this use case).
4. How do you reduce cloud cost by 30%?
   - Increase CDN TTL, reduce sampling rate of analytics logs (e.g., sample 10% of queries).
5. How do you support multi-region rollout?
   - Replicate the read path (Trie/Cache) across regions. Write path can consolidate to a central data lake for global popularity.

---

## 9. 🧩 Variants and Extensions

- Variant 1 (global users): Geo-localized Tries (e.g., separate Tries per language/region).
- Variant 2 (compliance-heavy): Strict PII filtering on raw logs before persistence.
- Variant 3 (realtime-first): Flink streaming pipeline for minute-level trending searches overlaid on top of batch results.
- Variant 4 (cost-optimized startup): Use a standard relational DB with prefix indexes and Heavy Redis caching instead of a custom Trie.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I skipped clarifying requirements
- [x] I did estimates that did not influence design
- [x] I added sharding/queueing without scale justification
- [x] I did not mention failure handling
- [x] I did not articulate trade-offs explicitly
- [x] I left no time for summary

---

## 11. 🧮 Scoring Rubric (Self-Evaluation)

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) | Your Score |
|---|---|---|---|---|
| Requirements handling | Vague | Mostly clear | Prioritized + quantified | 5 |
| Architecture clarity | Boxes only | Basic flow | End-to-end + failure-aware | 5 |
| Technical depth | Tool names | Some rationale | Pattern + metric-driven rationale | 5 |
| Trade-off quality | None | Some | Explicit and contextual | 5 |
| Communication | Disorganized | Understandable | Structured + concise | 5 |

---

## 12. ✅ Wrap-up Summary (Final 60-90 Seconds)

Use this closing pattern:
1. Restate key requirements and constraints: "We built a search autocomplete system aiming for <100ms latency at 48k QPS."
2. Summarize core architecture choice: "We separated the read and write paths, using an offline batch pipeline to build an optimized Trie with node-level caching."
3. Call out one intentional trade-off: "We traded strict real-time updates for eventual consistency to eliminate lock contention and guarantee read availability."
4. Mention one scale-evolution step: "As we scale, we can introduce prefix sharding for the Trie and a fast-path streaming job for trending topics."

---

## 📌 Final Checklist

- [x] Requirements and constraints captured
- [x] Estimates tied to decisions
- [x] APIs and entities are coherent
- [x] Read/write paths are explicit
- [x] Deep dive completed
- [x] Trade-offs stated
- [x] Follow-ups addressed
- [x] Strong summary delivered

---
**Real-world reference**: See how Airbnb solved this in the [Airbnb case study](../../case-studies/airbnb-search/)
