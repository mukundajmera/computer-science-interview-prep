# Ride Sharing — Interview Approach

## 1. Scope and Prioritize

- Lock core user flow: fare estimate -> request -> match -> trip lifecycle.
- State what is below-the-line to preserve time.

## 2. Quantify Load

- Convert location update frequency to write throughput.
- Estimate ride-request bursts in dense zones.

## 3. Define Core Entities and APIs

- Entities: `Ride`, `Driver`, `DriverLocation`, `SurgeZone`.
- APIs for estimate, request, driver actions, and status retrieval.

## 4. Draw Architecture

- Separate location ingestion path from command path.
- Add matching worker and availability index.

## 5. Deep Dives

1. Assignment correctness and idempotency.
2. Geo-index strategy and boundary lookups.
3. Surge and ETA update loops.

## 6. Wrap-Up

- Re-state strong consistency for assignment and eventual consistency for location freshness.
