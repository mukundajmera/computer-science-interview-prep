# 📋 Proximity Service - High Level Design

Use this template as a framework for practicing system design interviews.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- **System to design:** Proximity Service (e.g., Yelp, Google Places)
- **Core user value:** Allow users to discover nearby businesses based on location and let business owners manage profiles.

### Functional Requirements
- [x] FR1: Search businesses within radius $r$ (e.g., 5km) around `(latitude, longitude)`.
- [x] FR2: Business profile CRUD operations (infrequent write path).
- [x] FR3: Business detail lookup by ID.
- [x] FR4: Sort search results by distance.
- [x] FR5: Filter by category/rating.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Read latency | < 100 ms P99 (search queries) |
| Read/Write Ratio | 100:1 (Read-heavy) |
| Throughput | 20,000 search QPS, 200 write QPS |
| Consistency | Eventual consistency for business updates |
| Cache | Geo-distributed caching |

### Constraints
- Search latency is the most critical metric.
- Business profile writes are infrequent.

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | 100M | input |
| Search QPS | 20,000 | input |
| Write QPS | 200 | input |

### Storage

| Data Type | Avg Size | Total Volume | Notes |
|---|---|---|---|
| Business Profiles | 2.5 KB | 500 GB | 200M total businesses |
| Geohash Index | 16 bytes | 3.2 GB | Fits completely in Redis RAM |

### Decision Notes
- **Which estimate forces a design choice?** The tiny 3.2 GB index size means we can cache the entire geospatial index in memory (Redis), allowing ultra-fast searches and easily meeting the < 100ms latency target.

---

## 3. 🔌 API / System Interface

### Core Endpoints

```http
GET /api/v1/search/nearby?lat={lat}&lng={lng}&radius={radius_in_m}&category={category}&rating={rating}
```
**Response:** `[{ "business_id": "123", "name": "...", "distance": 450 }]`

```http
GET /api/v1/businesses/{id}
```
**Response:** Full business profile

```http
POST /api/v1/businesses
```
**Body:** `{ "name": "...", "lat": ..., "lng": ... }`

---

## 4. 🗄️ Core Entities and Data Model

### Data Schemas
```sql
CREATE TABLE businesses (
    business_id BIGINT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    address VARCHAR(512),
    city VARCHAR(100),
    geohash VARCHAR(12) NOT NULL,
    category VARCHAR(100),
    rating DOUBLE PRECISION,
    created_at TIMESTAMP NOT NULL,
    INDEX idx_geohash (geohash)
);
```

### Storage Choices
- **Primary DB:** PostgreSQL with PostGIS / Cassandra (stores business profiles as the source of truth).
- **Cache (Index):** Redis Sets (`Key: geohash:6_char -> Set of business_id`).
- **Cache (Profiles):** Redis Hashes (`Key: biz:<business_id> -> Hash of business profile`).

### Key Access Patterns
1. **Read path (Search):** Convert user `(lat, lng, radius)` to a Geohash, fetch matching business IDs from Redis, calculate exact distances, filter by category/rating, and enrich with profile data.
2. **Write path:** Update primary DB, recompute Geohash if location changed, push update to message queue for async cache invalidation/updates.

---

## 5. 🏗️ High-Level Architecture

![Architecture Diagram](diagrams/architecture.mmd)

### Component List
- **API Gateway:** Routes requests.
- **Location Search Service:** Stateless, computes Geohashes and queries Redis.
- **Business Profile Service:** Handles CRUD for profiles.
- **Redis Geohash Cache:** In-memory Geohash index and profile cache.
- **PostgreSQL with PostGIS / Cassandra:** Persistent storage.
- **Message Queue (Kafka):** Async propagation of business updates to the search index.

### Read Path (Search)
1. Client calls `GET /api/v1/search/nearby`.
2. Location Search Service calculates the central Geohash and 8 neighbors based on the radius.
3. Service queries Redis for all `business_id`s in those Geohashes.
4. Service fetches business profiles from Redis cache (or DB if miss).
5. Service filters exact distances, applies category/rating filters, sorts, and returns to client.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Spatial Indexing Trade-offs
- **Geohash:** Base32 string prefix encoding. Simple to implement and perfectly fits in Redis (String key -> Set of values). Supports quick boundary expansion by querying 8 neighbors. Best for this design.
- **QuadTree:** In-memory spatial tree splitting on business count. Great for variable density, but complex dynamic rebalancing and hard to update (requires tree locks and complex replication logic).
- **Google S2:** Hilbert curve encoding. Similar properties to Geohash but more complex to implement and generally better for very precise bounding boxes (e.g. mapping shapes) rather than simple radius searches.

### Deep Dive B: Cache Invalidation & Regional Replication
- **Cache invalidation:** Business profile changes (inserts/updates) are written to the database first via the Business Profile Service. A Change Data Capture (CDC) process or Kafka event then triggers a background worker to update the Redis Geohash cache and invalidate the profile cache.
- **Regional replication:** Due to the geo-distributed nature of the queries, we use geo-distributed caching. Data in Redis and PostgreSQL is partitioned by region (e.g., US-East vs US-West). Business updates in a region are replicated via Kafka to the corresponding region's cache.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now |
|---|---|---|---|
| Indexing | Geohash | QuadTree / Google S2 | Geohash is simpler to shard in Redis and perfectly fits the small index size. |
| DB Type | PostgreSQL with PostGIS / Cassandra | Pure NoSQL | PostGIS provides advanced spatial queries if needed as backup; Cassandra provides high write availability. Both are valid. |
| Cache strategy | Push-on-write | Pull-on-read | Read performance is critical. We pre-populate the cache on business creation. |

---

## 8. 🔮 Follow-up Questions
- See [FOLLOW-UPS.md](FOLLOW-UPS.md) for deeper interview probes on scale out and region handling.

---

## 9. 🧩 Variants and Extensions
- **Variant 1 (High Density):** In dense cities, length 6 Geohash might return too many results. Dynamically increase precision (e.g., length 7) for dense areas.
- **Variant 2 (Dynamic filtering):** Integrate Elasticsearch if users need complex text search ("Italian, open now, $$$") combined with location.

---

## 10. 🚨 Common Pitfalls (Self-Check)
- See [PITFALLS.md](PITFALLS.md) for typical mistakes.

---

## 11. 🧮 Scoring Rubric (Self-Evaluation)
- See [RUBRIC.md](RUBRIC.md) for interview evaluation dimensions.

---

## 12. 📚 Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
- [Comparison](COMPARISON.md)
- [Strong Answer](STRONG-ANSWER.md)

---
**Real-world reference**: See how Uber solved this in the [Uber case study](../../case-studies/uber-realtime/)
