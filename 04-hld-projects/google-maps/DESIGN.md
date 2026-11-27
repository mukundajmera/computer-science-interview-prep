# Google Maps & Navigation - High-Level Design

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: A global mapping and navigation system (Google Maps).
- Core user value: Seamless map viewing and accurate, traffic-aware navigation.

### Functional Requirements
- [ ] FR1: Map tile rendering across zoom levels (0 to 21).
- [ ] FR2: Route planning (fastest/shortest/avoid tolls).
- [ ] FR3: Turn-by-turn navigation with dynamic ETA.
- [ ] FR4: GPS location telemetry batching from mobile clients.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Read latency | < 50ms (map tiles), < 1s (route calculation) |
| Write latency | < 200ms (GPS telemetry ingestion) |
| Network | Global low-latency map tile CDN |
| Resilience | Resilient navigation during cellular disconnects |
| Durability | High (route graph and map tiles) |

### Out of Scope
- Local business search and reviews (covered in other designs)
- Street view image rendering

---

## 2. 📊 Back-of-Envelope Estimation

### Traffic

| Metric | Value | Formula |
|---|---|---|
| MAU | 1B | input |
| Nav Sessions | 50M concurrent | |

### Storage

| Data Type | Avg Size | Storage Volume |
|---|---|---|
| Map Tiles (Vector) | | ~100 TB (pre-rendered across 21 zoom levels) |

### Decision Notes
- Vector tiles over Raster PNGs: Raster tiles (~20KB) render poorly on rotation. Vector tiles (~5KB) transfer geometry rendered client-side, saving 75% bandwidth.
- Routing Algorithm: Standard Dijkstra is O(V log V + E), too slow globally. Hierarchical routing with Contraction Hierarchies (CH) precomputes shortcuts for sub-5ms routing.

---

## 3. 🔌 API / System Interface

### Core Endpoints

```http
POST /api/v1/telemetry
-- Request
{
  "user_id": "uuid",
  "locations": [
    {"timestamp": "iso8601", "lat": 37.7749, "lng": -122.4194, "speed": 15.5, "heading": 90.0}
  ]
}

POST /api/v1/routes
-- Request
{
  "origin": {"lat": 37.7749, "lng": -122.4194},
  "destination": {"lat": 37.3382, "lng": -121.8863}
}
-- Response
{
  "session_id": "nav_xyz",
  "eta_seconds": 3600,
  "route_path": [[lat, lng], [lat, lng], ...],
  "maneuvers": [...]
}

GET /api/v1/tiles/{z}/{x}/{y}.pbf
-- CDN cached map tiles
```

---

## 4. 🗄️ Core Entities and Data Model

### Data Schemas

```sql
-- User Location Telemetry (Cassandra)
CREATE TABLE user_location_telemetry (
    user_id UUID,
    timestamp TIMESTAMP,
    latitude DOUBLE,
    longitude DOUBLE,
    speed FLOAT,
    heading FLOAT,
    PRIMARY KEY (user_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
```

**Road Graph (Stored as Protobuf/Binary in S3 / In-Memory Cache)**
- Node: `{node_id: long, lat: double, lng: double}`
- Edge: `{edge_id: long, u: long, v: long, length_m: double, speed_limit: int, live_speed: int}`

**Active Navigation Session (Redis)**
- Key: `nav:session:<user_id>` -> `{route_tile_ids: [t1, t2, t3], dest_coord: [lat, lng]}`

### Storage Choices
- Telemetry DB: Cassandra (High write throughput, time-series friendly).
- Map Tiles: S3 + CDN (Immutable blob storage, high read volume).
- Route Graph Cache: In-memory distributed cache (Redis/Memcached or custom C++ service) for rapid graph traversal.

---

## 5. 🏗️ High-Level Architecture

### Read Path (Map Rendering & Routing)
1. **Map Tile Service:** Client requests map tile `/api/v1/tiles/{z}/{x}/{y}.pbf`. Uses Hierarchical QuadTree / Slippy Map tiles served via CloudFront/Akamai CDN. returns cached vector tile (<50ms).
2. **Routing Engine:** Client requests route via API Gateway. Road graph partitioned into hierarchical subgraphs (Contraction Hierarchies, A* search).
3. **Session:** Nav session state is stored in Redis.

### Write Path (Telemetry & Traffic)
1. **Telemetry:** Client batches GPS locations every 15-30s. POSTs to `/api/v1/telemetry`.
2. **Traffic Aggregation Service:** Live vehicle probe data streaming into Kafka, calculating segment speeds and dynamic ETAs.
3. **Processing:** Flink/Spark Streaming reads from Kafka.
    - Writes raw telemetry to Cassandra.
    - Map-matches GPS to road segments (edges).
    - Computes average speed per segment and updates the Live Traffic Service (In-Memory Graph Cache).
    - Triggers Reroute Service for active nav sessions if ETA changes significantly.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Routing Algorithm Trade-offs
- **Bottleneck:** Standard Dijkstra is prohibitively slow for long routes.
- **Chosen pattern:** Contraction Hierarchies (CH) + Routing Tiles.
- **Alternative considered:** A* search.
- **Trade-off accepted:** CH requires significant offline precomputation to build shortcut edges, but yields < 5ms query times at runtime, which is essential for low-latency initial routing and dynamic rerouting.

### Deep Dive B: Map Tile Serving
- **Bottleneck:** Serving tiles to 1B DAU requires massive bandwidth.
- **Chosen pattern:** Vector Protobuf Tiles over CDN.
- **Alternative considered:** Raster PNG Tiles.
- **Trade-off accepted:** Raster requires 20KB/tile and handles rotation poorly. Vector tiles (5KB/tile) shift rendering compute to the client GPU, drastically reducing bandwidth and S3 egress costs while providing smooth 3D rotation.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Map Tiles | Vector (Protobuf) | Raster (PNG) | Saves 75% bandwidth, client renders | Client GPU becomes a constraint |
| Telemetry Ingest | Kafka + Flink | Direct to DB | Buffers 1M QPS peaks, real-time map matching | Traffic aggregation needs change |
| Routing Algorithm | Contraction Hierarchies | Dijkstra / A* | Precomputes highways for sub-5ms queries | Precomputation pipeline gets too slow |
| Telemetry DB | Cassandra | PostgreSQL | Handles massive write volume (time-series) | Need complex relational queries |

---

## 8. 🔮 Follow-up Questions (Cross-links)
See [FOLLOW-UPS.md](./FOLLOW-UPS.md) for scaling and edge cases.

---

## 9. 🧩 Variants and Extensions
- Fleet Management: Heavy focus on bulk routing and precise vehicle telemetry.
- Logistics/Delivery: Traveling Salesman Problem (TSP) optimization for multiple stops.

---

## 10. 🚨 Common Pitfalls (Cross-links)
See [PITFALLS.md](./PITFALLS.md).

---

## 11. 🧮 Scoring Rubric (Cross-links)
See [RUBRIC.md](./RUBRIC.md).

---

## 12. 🛑 Bottlenecks and Failure Modes

Global navigation separates immutable map tile delivery from real-time telemetry and routing so degraded traffic pipelines never take down base routing or offline turn-by-turn guidance.

### Failure Modes

| Failure | Impact | Detection | Mitigation |
|---|---|---|---|
| Bad tile or routing-graph release | Broken turn-by-turn routes, wrong ETAs, or client tile decode errors | Canary region route-error rate, ETA drift alerts, and client decode-failure telemetry | Publish immutable versioned tile bundles and CH graphs (`v{N}`) to S3; flip manifest pointer back to `v{N-1}` |
| Traffic feed outage (Kafka/Flink lag) | Live segment speeds freeze; dynamic rerouting stalls | Kafka consumer lag, Flink checkpoint failures, and stale-edge age in Graph Cache | Degrade routing weights to time-of-day historical speeds and static `speed_limit` until live probes resume |
| Stale CDN map tiles | Clients render outdated road geometry after closures or map edits | Tile version mismatch counters and CDN cache-age telemetry | Use versioned tile URLs, targeted CDN edge purges for edited regions, and `stale-while-revalidate` TTLs |
| Routing graph cache node loss | Route calculation latency spikes above 1s SLA | Graph cache health checks, routing P99 latency alarms, and timeout rates | Route queries to healthy regional replicas; auto-warm replacement nodes from S3 CH snapshots before serving |
| Cellular disconnect or telemetry spike | Lost GPS pings or dropped reroute pushes for active drivers | Client upload error rate, API Gateway 5xx/429 spikes, and Redis session heartbeat gaps | Cache corridor tiles on device for offline turn-by-turn; buffer and retry GPS uploads on reconnect |

### Recovery and Rollback
- **Tile and routing-graph rollback:** Offline pipelines publish vector tiles and precomputed Contraction Hierarchies (CH) graphs to immutable versioned prefixes in S3 and roll them out region by region.
- **Atomic pointer switch:** If canary validation detects routing regressions or malformed protobuf tiles, operators roll back the active manifest pointer to `v{N-1}` without recomputing shortcuts.
- **Traffic outage degradation:** When Flink stream processing stalls, Routing Engines serve routes using historical time-of-day speed profiles and static edge speed limits rather than failing `/api/v1/routes`.
- **Navigation session recovery:** Active Redis sessions (`nav:session:<user_id>`) are treated as soft state; on shard failover, clients keep navigating from locally cached route geometry and re-register on the next sync.

### Retry and Replay
- **Idempotent telemetry retries:** Mobile clients batch GPS pings during cellular blackouts and retry `POST /api/v1/telemetry` with exponential backoff and jitter.
- **Safe upserts and DLQ:** Cassandra keys telemetry by `(user_id, timestamp)` so duplicate retries are idempotent upserts; malformed payloads route to a dead-letter queue (DLQ) for offline inspection.
- **Bounded stream replay:** After a Flink restart, consumers replay from committed Kafka offsets while dropping probe events older than a freshness window (e.g., 10 minutes) so stale traffic cannot overwrite current speeds.
- **Reroute push recovery:** If a reroute push times out or fails to reach a driver, the Reroute Service does not storm retries; the client reconciles updated ETAs and detours on its next periodic navigation poll.
