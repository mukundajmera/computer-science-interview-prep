# 🏆 Coach Answer: Ride Sharing — HLD

> **Type:** High-Level Design  
> **Difficulty:** Advanced  
> **Time Target:** 45 minutes

---

## Phase 1 — Requirements (5 min)

### Functional

1. Fare estimate.
2. Ride request.
3. Driver assignment.
4. Lifecycle tracking.

### Non-Functional

| Metric | Target |
|---|---|
| Match latency | < 60s |
| Assignment correctness | Strong |
| Location ingest latency | < 1s |
| Availability | 99.99% |

---

## Phase 2 — Capacity (5 min)

- 50M riders, 5M drivers.
- 1M concurrent rides.
- 10M+ location updates/minute.

---

## Phase 3 — APIs (5 min)

```http
POST /api/v1/fare-estimates
POST /api/v1/rides
POST /api/v1/rides/{rideId}/accept
POST /api/v1/drivers/location
```

---

## Phase 4 — Data Model (5 min)

- `Ride(ride_id, rider_id, driver_id, status, idempotency_key)`
- `Driver(driver_id, availability_state)`
- `DriverLocation(driver_id, lat, lng, ts)`

State machine: `REQUESTED -> MATCHED -> DRIVER_EN_ROUTE -> IN_PROGRESS -> COMPLETED/CANCELLED`

---

## Phase 5 — Architecture (10 min)

- Location ingestion path isolated from assignment path.
- Matching service uses geo index + availability index.
- Lifecycle transitions are strongly validated.

---

## Phase 6 — Deep Dives (10 min)

1. Assignment idempotency and offer loop.
2. Boundary-safe geospatial lookups.
3. Surge and ETA update loop.

---

## Phase 7 — Trade-Off Wrap (5 min)

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Assignment consistency | Strong | Eventual | Prevent duplicate assignments |
| Location consistency | Eventual | Strong | Better latency and throughput |
| Matching | Ranked candidates + retries | Single nearest | Better acceptance rate |
