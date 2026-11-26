# Ride Sharing — High-Level Design

Use this template as a framework for practicing system design interviews.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: A scalable ride-sharing platform (like Uber or Lyft) connecting riders with nearby drivers in real-time.
- Core user value: Quick, reliable, safe, and fairly priced point-to-point transportation at the push of a button.

### Functional Requirements
- [x] FR1: Drivers can broadcast their GPS locations continuously (e.g., every 4 seconds) to the system.
- [x] FR2: Riders can request a ride, specify pickup/dropoff, and get matched with an available nearby driver.
- [x] FR3: The system dynamically prices rides based on real-time local supply (drivers) and demand (riders) (Surge Pricing).
- [x] FR4: Riders and drivers can see the real-time status of the ride (e.g., requested, matching, in-progress, completed).
- [x] FR5: Drivers can accept or reject ride offers within a specific time window.
- [x] FR6: Riders can cancel their ride request before or after a driver has been matched.
- [x] FR7: Drivers can complete the ride once they reach the destination, triggering payment processing asynchronously.
- [x] FR8: Drivers can indicate their availability status (e.g., online, offline, taking a break).
- [x] FR9: Riders can review their past rides and download receipts.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% for core matching and ingest pipelines |
| Read latency | < 500ms for status updates and pricing queries |
| Write latency | < 50ms for location ingest (fire and forget) |
| Throughput | 250,000 location ingest QPS (Peak) |
| Consistency | Eventual consistency for locations, Strong for ride state transitions |
| Durability | Strict RDBMS durability for ride history and financial records |

### Constraints
- Regulatory/compliance: Data localization requirements in specific regions (e.g., GDPR in Europe, CCPA in California).
- Budget/cost preference: High cost-efficiency for the location ingest pipeline (cannot use expensive RDBMS for ephemeral data).
- Team/operational constraints: Standardize on Java/Go for services and PostgreSQL/Redis for data stores.
- Region/geography constraints: City-based geographical sharding to isolate regional failures and improve locality.

### Out of Scope
- Rider and driver rating systems (5-star ratings).
- Payment processing, billing, and driver payouts.
- Detailed routing algorithms, traffic prediction, and ETAs (assume an external Maps API like Google Maps is used).

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

*(Note: All supplied workload values are an explicit illustrative scenario, not a universal scale benchmark. Recomputing core sizing below.)*

### Traffic

| Metric | Value | Formula |
|---|---|---|
| Active Drivers | 1,000,000 | System-wide peak active drivers |
| Location Ingest Rate | Every 4 seconds | Frequency of GPS updates per driver |
| Ingest QPS | 250,000 | 1,000,000 drivers / 4 seconds |
| Ride Request Attempts | 60,000 / min | Total request attempts (60,000 / 60 = 1,000 req/s avg). Peak is 1,000 * 1.5 = 1,500 req/s |
| Successful Rides | 50,000 / min | Successful completed operations (50,000 / 60 = 833.3 req/s avg). Peak is 833.3 * 1.5 = 1,250 req/s |
| State Updates | ~3,666 QPS | (50k successful * 4 states + 10k failed * 2 states) / 60 |
| WebSocket Connections | 2,000,000 | 1M drivers + 1M riders actively using the app |

### Storage and Bandwidth

| Data Type | Avg Size | Calculation (Average and Peak) | 1-Year Storage |
|---|---|---|---|
| Ingest Bandwidth | 128 bytes | **Avg:** 250,000 QPS * 128 B = 32 MB/s.<br>**Peak:** 375,000 QPS * 128 B = 48 MB/s. | N/A (Streaming) |
| Ride Attempt Storage | 1 KB | **Avg:** 60,000 attempts/min * 60 min * 24 hr = 86,400,000 attempts/day. 86.4M * 1 KB = 86.4 GB/day. | 86.4 GB/day * 365 = ~31.5 TB/yr |
| Successful Ride Storage| 1 KB | **Avg:** 50,000 success/min * 60 min * 24 hr = 72,000,000 rides/day. 72M * 1 KB = 72 GB/day. | 72 GB/day * 365 = ~26.2 TB/yr |
| Geo Index (Redis) | 100 bytes | **Avg:** 1,000,000 drivers * 100 B = 100 MB RAM | N/A (Transient) |

### Decision Notes
- Which estimate forces a design choice? The 250,000 QPS ingest rate makes writing directly to a traditional RDBMS impossible without massive, expensive sharding. It mandates a stream processing architecture (e.g., gRPC -> Kafka -> Flink -> Redis).
- What assumption is most uncertain? The exact spatial distribution of drivers per city; some cities may have intense "hotspots" (e.g., after a concert) requiring dynamic, finer-grained spatial partitioning to avoid hot shards in Redis.
- What about memory limits for Redis? With 1M drivers at 100 bytes each, the memory requirement is incredibly small (~100MB). We will be bounded by network I/O or CPU before RAM, allowing us to provision cost-effective nodes.
- What about the network throughput? 32 MB/s ingest bandwidth is easily handled by modern cloud provider networks, but requires horizontal scaling at the API Gateway layer to handle the sheer number of concurrent TLS connections (1M+ concurrent WebSockets/gRPC streams).
- What about historical storage? Storing 26TB/yr in PostgreSQL is feasible with table partitioning by month, but long-term analytics should be offloaded to a data warehouse (like Snowflake or BigQuery) using Change Data Capture (CDC).

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: 
  - gRPC for mobile-to-gateway (efficient binary serialization, multiplexing, lower battery usage).
  - REST for public/admin APIs.
  - WebSockets/Server-Sent Events (SSE) for realtime ride status updates to the client.
- Auth model: OAuth 2.0 with short-lived JWT tokens.
- Rate limiting policy: Token bucket, strictly enforced per user/driver ID at the API Gateway.

### Core Endpoints
```http
POST /api/v1/rides
{
  "pickup_lat": 37.7749,
  "pickup_lng": -122.4194,
  "dropoff_lat": 37.3382,
  "dropoff_lng": -121.8863,
  "ride_type": "uber_x",
  "idempotency_key": "req-abc-123"
}

POST /api/v1/rides/{rideId}/accept
{
  "driver_id": "drv-456",
  "location": {"lat": 37.7750, "lng": -122.4190}
}

POST /api/v1/rides/{rideId}/start
POST /api/v1/rides/{rideId}/complete
POST /api/v1/drivers/location
{
  "driver_id": "drv-456",
  "lat": 37.7750,
  "lng": -122.4190,
  "timestamp": "2023-10-01T12:00:00Z"
}
```

### Error Model
- `400` invalid input (e.g., invalid coordinates, missing fields).
- `401/403` auth/authz missing, expired token, or insufficient permissions.
- `404` missing resource (e.g., ride ID not found).
- `409` conflict/concurrency (e.g., double-dispatch attempt, driver already accepted another ride).
- `429` throttled (e.g., too many location updates from a single client).
- `5xx` internal dependency failure (e.g., matching service timeout).

### Explicit Core Contract: Ride Assignment (Consistency Boundary)
The core `accept_ride` API must enforce an explicit consistency boundary using optimistic concurrency to prevent double-dispatch (two drivers successfully accepting the same ride). The normal worked trace assumes the ride is in the `MATCHING` state and transitions it to `ASSIGNED`, verifying the initial state and idempotency.

#### Java Implementation
```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.Map;
import java.util.Objects;

public class RideAssignmentContract {
    // In-memory simulation of PostgreSQL rides table with optimistic locking
    private static final Map<String, RideRecord> RIDES_DB = new ConcurrentHashMap<>();

    public static class RideRecord {
        public String rideId;
        public String status;
        public String driverId;
        public int version;
        
        public RideRecord(String rideId, String status, int version) {
            this.rideId = rideId;
            this.status = status;
            this.version = version;
        }
    }

    public static class AcceptResult {
        public boolean success;
        public String message;
        public AcceptResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }
    }

    /**
     * Normal Worked Trace: Driver accepts an available ride.
     * Consistency Boundary: Uses synchronized block (simulating SQL version increment and row lock) 
     * to strictly prevent concurrent double-assignments.
     */
    public static AcceptResult acceptRide(String rideId, String driverId, int expectedVersion) {
        RideRecord current = RIDES_DB.get(rideId);
        
        // 1. Validate existence
        if (current == null) {
            return new AcceptResult(false, "Ride not found");
        }
        
        // 2. Validate current state machine boundary
        if (!"MATCHING".equals(current.status)) {
            // Check for idempotency: if this driver already accepted it
            if ("ASSIGNED".equals(current.status) && Objects.equals(current.driverId, driverId)) {
                return new AcceptResult(true, "Idempotent retry: Already assigned to this driver");
            }
            return new AcceptResult(false, "Ride is no longer available for matching");
        }
        
        // 3. Apply explicit consistency boundary (Optimistic Concurrency)
        synchronized (current) {
            if (current.version == expectedVersion && "MATCHING".equals(current.status)) {
                current.status = "ASSIGNED";
                current.driverId = driverId;
                current.version++;
                return new AcceptResult(true, "Successfully assigned ride");
            }
        }
        
        return new AcceptResult(false, "Concurrency conflict: Ride was updated by another process");
    }
}
```

#### Python Implementation
```python
import threading
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

@dataclass
class RideRecord:
    ride_id: str
    status: str
    driver_id: Optional[str]
    version: int
    lock: threading.Lock

# In-memory simulation of PostgreSQL rides table with optimistic locking
RIDES_DB: Dict[str, RideRecord] = {}

def accept_ride(ride_id: str, driver_id: str, expected_version: int) -> Tuple[bool, str]:
    """
    Normal Worked Trace: Driver accepts an available ride.
    Consistency Boundary: Uses atomic check-and-set (simulating SQL version increment and row lock) 
    to strictly prevent concurrent double-assignments.
    """
    current = RIDES_DB.get(ride_id)
    
    # 1. Validate existence
    if not current:
        return False, "Ride not found"
        
    # 2. Validate current state machine boundary
    if current.status != "MATCHING":
        # Check for idempotency: if this driver already accepted it
        if current.status == "ASSIGNED" and current.driver_id == driver_id:
            return True, "Idempotent retry: Already assigned to this driver"
        return False, "Ride is no longer available for matching"
        
    # 3. Apply explicit consistency boundary (Optimistic Concurrency)
    with current.lock:
        if current.version == expected_version and current.status == "MATCHING":
            current.status = "ASSIGNED"
            current.driver_id = driver_id
            current.version += 1
            return True, "Successfully assigned ride"
            
    return False, "Concurrency conflict: Ride was updated by another process"
```

---

## 4. 🗄️ Core Entities and Data Model

### Core Entities
- Entity A: `Ride` (Stores the lifecycle of a trip from request to completion).
- Entity B: `Driver` (Driver profile, vehicle details, and current state).
- Entity C: `DriverLocation` (Ephemeral GPS data used for matching).

### Storage Choices
- Primary DB: PostgreSQL with PostGIS for ride state and complex spatial analytics (reason: ACID guarantees for ride state, robust transactional support, spatial extensions).
- Cache/Index: Redis Cluster (reason: Low latency data structures for geospatial indexing and transient driver state).
- Async Pipeline: Apache Kafka (reason: High throughput, durable buffer for location updates).

### Key Access Patterns
1. Read path query: Rider apps poll or listen for `Ride` state changes via WebSockets.
2. Write path mutation: Strict FSM transitions on `Ride` (e.g., REQUESTED -> MATCHING -> ASSIGNED -> IN_PROGRESS).
3. Secondary lookup: Matching service querying Redis for all available drivers within a specific H3 hexagon.

### PostgreSQL/PostGIS Schema (Rides)
```sql
CREATE TABLE rides (
    ride_id UUID PRIMARY KEY,
    rider_id UUID NOT NULL,
    driver_id UUID,
    status VARCHAR(20) NOT NULL, -- REQUESTED, MATCHING, ASSIGNED, ARRIVED, IN_PROGRESS, COMPLETED, CANCELLED
    pickup_geom GEOMETRY(Point, 4326) NOT NULL,
    dropoff_geom GEOMETRY(Point, 4326) NOT NULL,
    price_estimate DECIMAL(10, 2),
    actual_price DECIMAL(10, 2),
    version INT DEFAULT 1, -- For Optimistic Concurrency Control
    idempotency_key VARCHAR(64) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_rides_status ON rides(status);
CREATE INDEX idx_rides_driver ON rides(driver_id);
CREATE INDEX idx_rides_rider ON rides(rider_id);

CREATE TABLE drivers (
    driver_id UUID PRIMARY KEY,
    name VARCHAR(100),
    vehicle_info VARCHAR(100),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Redis Key Schema
- Location Index: `driver_loc:{h3_index}` -> Redis Hash mapping `{ driver_id: {lat, lng, timestamp} }`
- State Index: `driver_state:{driver_id}` -> String (e.g., "AVAILABLE", "ON_TRIP", "OFFLINE")
- Surge Multiplier: `surge:{h3_index}` -> Float (e.g., 1.5)

---

## 5. 🏗️ High-Level Architecture

### Component List
- API Gateway: Netty/gRPC gateways terminating mobile connections, handling TLS, Auth, and Rate Limiting.
- Ingestion Pipeline: Kafka topics for buffering raw location updates.
- Stream Processor: Flink jobs computing spatial indexes, aggregating supply/demand, and calculating surge pricing.
- Stateful Services: Ride Service (FSM orchestrator), Matching Service, Location Service.
- Data Stores: Redis Cluster (Geo Index), PostgreSQL (Ride DB).

### Driver Location Ingest Pipeline
1. Driver app sends location via gRPC to the Netty Gateway every 4 seconds.
2. Gateway authenticates the request and drops the payload into a partitioned Kafka topic (`driver-locations`).
3. Apache Flink spatial stream processor reads from Kafka, assigns the coordinates to an H3 index, and updates the corresponding Redis cluster partition (H3 cell).
4. Simultaneously, a separate Flink job aggregates driver counts per H3 index into a tumbling window (e.g., 1 minute) to compute the local supply metric for surge pricing.
5. The Flink jobs are stateful and periodic, checkpointing their state to persistent storage (like S3) to ensure exact-once semantics.
6. The location ingest process is completely fire-and-forget from the perspective of the mobile client, minimizing latency overhead on the driver's device.

### Read Path (Rider App checking status)
1. Rider app establishes a WebSocket connection to the API Gateway.
2. Gateway routes the subscription request to the Notification Service.
3. The Notification Service listens to Redis Pub/Sub channels (or a Kafka topic for state changes) and pushes the updated ride state and driver location down to the client.
4. Clients periodically fall back to HTTP GETs if WebSockets disconnect, reading directly from the Ride DB via the Ride Service.

### Write Path (Ride Request and Matching)
1. Rider requests a ride; the Ride Service creates a `REQUESTED` record in PostgreSQL. The `idempotency_key` prevents duplicate charges if the client retries.
2. The Ride Service transitions the state to `MATCHING` and enqueues a matching task.
3. The Matching Service queries Redis for available drivers in the rider's H3 hexagon (and adjacent k-ring neighbors).
4. The Matching Service runs the Two-Sided Matching Algorithm (greedy or batched).
5. The selected driver app is notified via push notification/WebSocket.
6. Upon driver acceptance, the Ride Service updates the DB to `ASSIGNED` using optimistic locking to ensure no other driver claimed it.

### Additional Architectural Considerations
When considering the API Gateway, we must also think about connection management for millions of WebSockets. Netty is excellent here, but we must ensure TCP keep-alives are properly tuned to avoid dropping idle connections while preventing ghost connections from consuming file descriptors. A custom heartbeat mechanism (e.g., application-level Ping/Pong every 30 seconds) is often layered on top of WebSockets.

For the Kafka cluster handling 250,000 QPS, we need to carefully design our partitioning strategy. Partitioning by `driver_id` ensures that all location updates for a specific driver go to the same partition, maintaining strict ordering. This ordering is critical for Flink to calculate accurate vectors (speed and heading). If we partitioned by H3 index, a driver crossing a boundary would switch partitions, potentially causing out-of-order processing and velocity miscalculations.

### Failure Modes and Recovery
- **Trace 1: Driver disconnect during trip (late location update):** Mobile apps cache the trip state locally. The PostgreSQL Ride DB holds the authoritative truth and owns the state. If the driver app drops offline during the `IN_PROGRESS` state, the ride and driver states are fully preserved. When the driver reconnects and sends a late location update, they simply fetch the active trip state from the Gateway and resume, retaining the strict `IN_PROGRESS` assignment without interruption.
- **Trace 2: Network partition between dispatch and driver app:** During the `ASSIGNED` step, a network partition could block the driver's accept/reject reply. PostgreSQL owns the state. The Matching service sets a strict 15-second timeout on the assignment lock. If a timeout occurs (or a reply drops), the server replays the ride state to the dispatch queue, returning the ride to the `MATCHING` state. The optimistic concurrency lock prevents double-dispatch if the driver's delayed accept arrives later, ensuring the true guarantee is singular ride assignment.
- Redis shard crash recovery: Redis Cluster handles automatic master-replica failover. Because location data is highly ephemeral (updated every 4s), even if a shard suffers complete data loss, the new primary will repopulate its geo-index from the incoming Kafka streams almost instantly.
- Kafka broker failure: Topics are replicated (Replication Factor = 3). Flink maintains consumer offsets in checkpoints to ensure exact-once processing semantics during recovery.
- Service deployment rollback: The matching and ride services must be stateless and gracefully degradable. If a new deployment has a bug, we can instantly rollback without state loss.
- PostgreSQL Primary Failure: In the event the primary PostgreSQL instance goes down, a replica must be promoted. During this failover window (typically 10-30 seconds), ride requests and state transitions will fail or queue. We must design the API gateway and mobile clients to handle `503 Service Unavailable` or `504 Gateway Timeout` with exponential backoff and jitter. We should not attempt to mask this by caching write intents, as ride matching requires immediate consistency to prevent double-booking.
- Notification Service Degradation: If the WebSocket push infrastructure becomes overloaded, the mobile applications should seamlessly fall back to HTTP long-polling or standard short-polling. This requires the client to detect missed heartbeats or timeouts and initiate a `GET /api/v1/rides/{rideId}/status` request. While polling increases backend load, it ensures the core user journey can complete even if the real-time push layer fails.
- Geocoding/Maps API Outage: The system relies on external APIs (like Google Maps) for routing and ETAs. If this external dependency fails, we must fall back to a less accurate, internal heuristic. For instance, we can calculate the straight-line (haversine) distance between pickup and dropoff, multiply by a city-specific "tortuosity factor" (e.g., 1.4 to account for road curvature), and estimate time using average historical speeds for that H3 hex. This degraded mode allows rides to continue while the third-party provider is down.
- Redis Leader Failure: Standard leader-follower replication is used in the Redis cluster. If a leader node fails, Redis Sentinel will automatically promote a follower. The brief downtime is mitigated by the application retrying queries, and state is quickly rebuilt.
- Flink Job Failure: Flink relies on ZooKeeper for leader election and JobManager high availability. If a TaskManager fails, Flink restarts the affected tasks on a new slot from the last successful checkpoint, guaranteeing exact-once processing and minimal downtime.
- DLQ (Dead Letter Queue): Any Kafka messages that fail validation or trigger unhandled exceptions in the Flink pipeline are routed to a DLQ topic for manual inspection and potential replay to avoid blocking the main stream.
- Datacenter Loss: We run active-active in multiple availability zones within a region. If a whole region goes down, we redirect traffic via Route53 to a standby region, accepting the loss of active volatile location data but preserving state via cross-region PostgreSQL replication.

---

## 6. 🔍 Deep Dives (Pick 1-2)

### Deep Dive A: Geospatial Indexing Comparison
- Bottleneck: Querying 1,000,000 moving drivers to find the closest available one in < 50ms requires a highly efficient spatial index.
- Chosen pattern: Uber H3 (hexagonal hierarchical spatial index). We use resolutions 7 (edge length ~1.2km), 8 (~460m), or 9 (~170m) depending on urban density (resolution 7-9 is a scenario choice, not a universal city setting, and average edge lengths are approximate/global table values, not actual drive radii).
- Alternative considered: Geohash (base32 string prefixes of interleaved Z-order curves) and QuadTree (hierarchical tree of squares).
- Trade-off accepted: We compare H3, Geohashes, and QuadTrees on several dimensions. Geohash uses rectangular grids, meaning diagonals are further away than adjacent sides, creating directional distortion. Geohashes also suffer from edge cases where physically close points have no common string prefix at major boundaries. QuadTrees suffer from similar boundary and diagonal distortion issues. H3 uses hexagons (and 12 pentagons across the globe) offering exactly one distance between a cell center and all immediate neighbors. While H3 minimizes directional/geometric distortion compared to grid structures, it does not eliminate it completely due to cell-size variation and the presence of pentagons (which cause edge effects). H3 index hierarchy also allows for straightforward neighbor structure searches (k-ring searches). However, one must calculate local drive distances, as H3 table values only represent approximate mathematical edge lengths.
- Implementation Note: H3 indexes are stored in Redis as the key (`driver_loc:{h3_index}`), mapping to a Redis Hash. This allows O(1) lookups for all drivers in a specific hexagon. We update a driver's location by deleting them from the old H3 Hash and inserting them into the new one.

### Deep Dive B: Two-Sided Matching Algorithm
- Bottleneck: Greedily matching the absolutely closest driver to a request can lead to global inefficiencies (e.g., driver A takes rider X, leaving driver B very far from rider Y, increasing total system wait time).
- Chosen pattern: 10-second batch optimization using a bipartite maximum-weight matching algorithm (such as the Hungarian algorithm or a min-cost flow solver).
- Trade-off accepted: We delay the match by up to 10 seconds to collect a pool of ride requests and a pool of available drivers. This minimizes global wait times across the system by finding the globally optimal pairing of `N` drivers to `M` riders. The candidate set must be bounded within the 10-second matching window; the Hungarian assignment does not scale as an unbounded all-driver/all-rider solve due to its O(N^3) cost constraints. If the batch optimization misses its latency deadline (e.g., due to computational overload), we gracefully degrade to a greedy nearest-neighbor approach as a fallback.
- Optimizing further: We can add an ML-based heuristic that predicts driver movement and rider requests based on historical data. This predictive matching could dispatch drivers to expected high-demand areas slightly before the requests actually occur.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Geospatial Index | Uber H3 | Geohash/QuadTree | Eliminates directional distortion; uniform neighbor distance; open-source. | If H3 library performance degrades in our specific stack. |
| Ingest DB | Redis (In-Memory) | Cassandra | 250k QPS is easily handled in-memory; data is highly ephemeral. | If we need to query historical driver tracks directly without a data warehouse. |
| Matching Strategy | 10-second Batched | Immediate Greedy | Reduces global wait times significantly at peak hours. | If user conversion drops due to the 10s matching delay. |
| FSM Concurrency | Optimistic Locking | Pessimistic Locking | Read-heavy system; avoids holding DB locks during slow network calls to drivers. | If we see high contention/retries on single ride rows (unlikely). |
| Transport Protocol | gRPC (Mobile) | REST/JSON | Low overhead and binary serialization saves battery and network transfer for constant pings. | If our external client ecosystem cannot support gRPC properly. |

---

## 8. 🔮 Follow-up Questions

1. What changes at 10x scale?
   - Moving from city-based logical sharding to physical cell-based routing architectures (like Uber's Ringpop) to distribute stateful matching logic directly across nodes based on H3 indexes, removing the need for a central monolithic matching service.
2. What fails first under a regional outage?
   - Active rides lose state visibility. We would need multi-region active-active databases (e.g., CockroachDB or Google Spanner) for the core Ride DB to survive a full AZ/Region drop without losing active trips.
3. How does the design change for strict consistency?
   - For rides, we already use PostgreSQL for strict consistency. For locations, strict consistency is unnecessary and would break the system due to the sheer volume of updates.
4. How do you reduce cloud cost by 30%?
   - Implement adaptive location pinging: drivers moving slowly or in low-demand areas ping every 10-15 seconds instead of every 4 seconds, drastically reducing ingest bandwidth and processing.
5. How do you support multi-region rollout?
   - Deploy isolated stacks per continent (e.g., NA-East, EU-West) since drivers in Paris cannot pick up riders in New York. This simplifies compliance and latency.
6. What happens if the driver's phone dies during a trip?
   - The rider app will continue to poll the backend. Because location updates stop, the ETA will pause. The backend Ride Service detects a missed heartbeat from the driver and alerts the rider. The ride remains in `IN_PROGRESS` until the driver reconnects or support intervenes.
7. How do you prevent fraud or GPS spoofing?
   - We implement a velocity check algorithm in the Flink processing pipeline. If the distance between two sequential location pings divided by the time elapsed implies an impossible speed (e.g., >200 mph), the ping is dropped and a fraud alert is raised for that driver.
8. How does the system handle "phantom rides" where drivers never pick up the rider?
   - The FSM mandates a geospatial proximity check before allowing the `ARRIVED` state transition. The driver's location must be within X meters of the `pickup_geom` for the state change to be accepted by the Ride Service.
9. How is data partitioned in PostgreSQL?
   - `rides` table is partitioned by `created_at` (e.g., monthly). To scale horizontally, we can use a Distributed SQL database like CockroachDB, sharded by `city_id` and `ride_id` to ensure operations in the same city are colocated on the same nodes.
10. How do you migrate from REST to gRPC without downtime?
    - Implement a proxy layer or Gateway that supports both. Dual-write or dual-read during a phased migration of client apps, gradually deprecating the REST endpoints via API versioning.

---

## 9. 🧩 Variants and Extensions

- Variant 1: Dynamic Surge Pricing with Spatial Smoothing. The Flink stream processor computing the surge pricing operates on a tumbling window. Let's break down the mechanics:
  1. **Supply Calculation**: Flink counts unique `driver_id`s broadcasting `AVAILABLE` status within each H3 hex over a 1-minute window.
  2. **Demand Calculation**: Flink consumes a separate Kafka topic (`ride-requests`) and counts the number of new `REQUESTED` events per H3 hex over the same window.
  3. **Ratio Computation**: The raw surge multiplier is calculated as `f(Demand / Supply)`. If Supply is 0, the multiplier is capped at a system maximum (e.g., 3.0x).
  4. **Spatial Smoothing**: To prevent "surge cliffs" (where a rider crosses a street and the price halves), we apply a Gaussian blur-like algorithm. The final surge for a hex is a weighted average of its raw surge and the raw surges of its immediate k-ring neighbors.
  5. **Temporal Smoothing**: To prevent prices from fluctuating wildly every minute, we apply an Exponential Moving Average (EMA) to the smoothed spatial value. `Current_Surge = (alpha * New_Surge) + ((1 - alpha) * Previous_Surge)`.
  6. **Publishing**: The final computed surge values are written to Redis (`surge:{h3_index}`) where the Ride Service queries them when generating upfront prices for new requests.
- Variant 2: Finite State Machine with Optimistic Concurrency. Ride state transitions (REQUESTED -> MATCHING -> ASSIGNED -> ARRIVED -> IN_PROGRESS -> COMPLETED) require a `version` column in PostgreSQL to prevent double-dispatch (e.g., two drivers attempting to accept the exact same ride concurrently). This allows lock-free atomic updates: `UPDATE rides SET status = 'ASSIGNED', driver_id = 'drv-456', version = version + 1 WHERE ride_id = 'req-123' AND version = 1`.
- Variant 3: Machine Learning ETA Prediction. Integrating historical traffic data and weather models into the routing engine to provide highly accurate upfront pricing and ETAs, replacing basic distance-based heuristics.
- Variant 4: Scheduled Rides. Handling rides scheduled hours in advance requires a distinct workflow. Instead of immediate matching, requests are stored in PostgreSQL with a scheduled time. A cron-like scheduler (e.g., Quartz or Temporal) wakes up 15-20 minutes before the pickup time, transitions the ride to `MATCHING`, and injects it into the standard matching pool, potentially with a higher priority or guaranteed minimum surge to incentivize drivers.
- Variant 5: Carpooling (UberPOOL/Lyft Line). This significantly complicates the matching algorithm, requiring multi-stop route optimization (e.g., solving variations of the Dial-a-Ride Problem) to match riders with overlapping routes while adhering to strict time-window constraints.
- Variant 6: Real-time driver positioning on map. Rather than returning raw coordinates to the client, the backend could push "snapped-to-road" coordinates processed via an external mapping service to prevent the driver's icon from appearing to drive through buildings on the map UI.
- Variant 7: Handling high-density events. For events like stadium concerts, point-to-point matching breaks down due to traffic gridlock. The system should switch to a "FIFO Queue" or "PIN code" dispatch model where riders walk to a designated pickup zone and enter a PIN generated by the first driver they physically meet.
- Variant 8: Regulatory Data Retention. Certain cities require 7-year retention of all ride records for tax and audit purposes. We implement an asynchronous CDC pipeline using Debezium to stream ride updates from PostgreSQL to an immutable AWS S3 bucket in Parquet format, governed by strict IAM retention policies.
- Variant 9: VIP Dispatch Policies. The system may configure priority queues for VIP riders or top-rated drivers. This alters the bipartite graph weights in the matching algorithm to favor these premium users, ensuring they experience the lowest possible wait times.
- Variant 10: Asynchronous Payment Processing. Upon the `COMPLETED` state transition, the Ride Service publishes an event to Kafka. The Billing Service consumes this, charges the rider's stored payment method via Stripe/Braintree, and updates a separate `payments` table.
- Variant 11: Real-time safety monitoring. By tapping into the Kafka location stream, a real-time safety service can detect unusual stops (e.g., on a highway) or deviations from the expected route, automatically prompting the rider and driver via push notification to confirm their safety.
- Variant 12: Heatmaps for Drivers. The application computes aggregate demand per H3 cell and exposes it to drivers as a heatmap to help them position themselves optimally, matching real-time supply to predictive demand.
- Variant 13: Edge AI Matching. Moving some preliminary matching logic directly to the mobile device using federated learning, reducing backend load and improving latency in poor network conditions.
- Variant 14: Geo-fenced Pricing Zones. Specialized logic for airports or event venues where dynamic pricing is overridden by flat rates or geofence-specific formulas.
- Variant 15: Cross-border rides. Handling rides that cross international borders requires multi-currency support, tax calculation adjustments, and potentially switching backend routing nodes.

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

## 11.5 Requirement-to-Section Review

- **1) Capacity Planning Math:** Covered in **"2. 📊 Back-of-Envelope Estimation"**. Included 1M drivers / 4s = 250k QPS, 50k req/min = 833.3/s, and 32 MB/s application payload limits. Values noted as illustrative scenarios, not absolute scale benchmarks.
- **2) Geospatial Indexing Comparison:** Covered in **"Deep Dive A: Geospatial Indexing Comparison"**. Compares H3 vs. Geohash vs. QuadTree, explicitly detailing neighbor structure, boundaries, pentagons, and why it doesn't eliminate all geometric distortion. Resolves 7-9 as a scenario choice.
- **3) Driver Location Ingest Pipeline:** Covered in **"5. 🏗️ High-Level Architecture (Driver Location Ingest Pipeline)"**. Traces Netty -> Kafka -> Flink -> Redis cluster (H3 cell partitions).
- **4) Two-Sided Matching Algorithm:** Covered in **"Deep Dive B: Two-Sided Matching Algorithm"**. Discusses greedy nearest-neighbor vs 10-second batch optimization, bounding candidate sets, latency fallback, and why Hungarian O(N^3) assignment doesn't scale unbounded.
- **5) Dynamic Surge Pricing:** Covered in **"9. 🧩 Variants and Extensions (Variant 1)"**. Includes Supply/Demand ratio per H3, and spatial/temporal smoothing to avoid boundary price cliff effects.
- **6) Finite State Machine:** Covered in **"4. 🗄️ Core Entities and Data Model"** and **"9. 🧩 Variants and Extensions (Variant 2)"**. Traces REQUESTED -> MATCHING -> ASSIGNED -> ARRIVED -> IN_PROGRESS -> COMPLETED with optimistic concurrency locks.
- **7) Data Models and API:** Covered in **"3. 🔌 API / System Interface"** and **"4. 🗄️ Core Entities and Data Model"**. Includes PostgreSQL/PostGIS schemas, Redis key schemas, HTTP/WebSocket API endpoints.
- **8) Failure modes:** Covered in **"5. 🏗️ High-Level Architecture (Failure Modes and Recovery)"**. Traces driver disconnect during trip (retaining state) and network partition (timeout/replays, who owns state, double dispatch prevention).

---

## 12. ✅ Wrap-up Summary (Final 60-90 Seconds)

1. Restate key requirements: We designed a ride-sharing backend capable of ingesting 250,000 driver location updates per second while ensuring strict, correct state transitions for ride assignments.
2. Summarize core architecture: We decoupled the ephemeral, high-throughput location data (handled via gRPC -> Kafka -> Flink -> Redis) from the strongly consistent transactional data (Ride Service -> PostgreSQL).
3. Call out one intentional trade-off: We chose a batched matching algorithm, trading a few seconds of initial matching latency for a globally optimal match that significantly reduces overall wait times and deadhead miles for drivers.
4. Mention one scale-evolution step: As we grow, we will implement dynamic polling intervals for idle drivers and spatial smoothing for our surge pricing to prevent boundary cliffs.

---

## Related

- [PROBLEM](./PROBLEM.md)
- [RUBRIC](./RUBRIC.md)
- [FOLLOW-UPS](./FOLLOW-UPS.md)
- [STRONG-ANSWER.md](./STRONG-ANSWER.md)

---
**Real-world reference**: See how Uber solved this in the [Uber case study](../../case-studies/uber-realtime/)
