# Google Maps & Navigation - Follow-Up Questions

## Follow-up questions

1. **How do you handle routing when a user goes entirely offline?**
   - *Answer:* The client application must preemptively download a generalized version of the route graph (and surrounding vector tiles) for the planned corridor. If the user deviates from the path while offline, the client performs local, simplified routing on the downloaded subset of the graph.

2. **How do you detect road closures based purely on user telemetry?**
   - *Answer:* If the stream processor (Flink) detects that historically busy road segments suddenly have zero traversal events (despite active users in the immediate vicinity), or if users continuously reroute away from a specific segment, it flags an anomaly. A confidence threshold must be met before updating the live graph cache to "closed".

3. **How does the system scale to support hyper-local, sudden traffic spikes (e.g., a stadium emptying)?**
   - *Answer:* The ingestion pipeline (Kafka) absorbs the burst. The stream processor dynamically scales up task slots to process the hot partitions. The map-matching logic aggressively aggregates the dense signals into a single "severe congestion" penalty on the affected edges, triggering reroutes for other users to avoid the area.

## Variants and extensions

- **Ride-Sharing (Uber/Lyft):** While similar, ride-sharing requires precise ETA calculation for pick-ups and spatial indexing (e.g., H3 or S2) to rapidly pair drivers and riders within a radius, rather than just A-to-B routing.
- **Logistics & Delivery:** Extends routing to the Traveling Salesman Problem (TSP) or Vehicle Routing Problem (VRP). The backend must compute optimal order sequences for dozens of stops, often relying heavily on offline batch processing rather than sub-second real-time queries.

## Interviewer probes to prepare

- "If Contraction Hierarchies require massive offline precomputation, how do you handle a sudden road closure that changes the graph?"
  - *Probe response:* Standard CH struggles with dynamic weights. To handle live traffic, we often use variants like *Customizable Route Planning (CRP)*, which separates the static topology from the dynamic edge weights, allowing metric updates in real-time without full recomputation.
