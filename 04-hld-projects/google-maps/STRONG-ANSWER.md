# Google Maps & Navigation - Strong Answer

## Core Philosophy
A strong answer explicitly divides the architecture into two distinct data flows: the massive, cache-friendly read path for map rendering, and the high-throughput, stream-processed write path for real-time telemetry and dynamic routing.

## 1. Requirements & Sizing
> Say: "To design Google Maps at a 1B DAU scale, we must solve for two very different workloads. First, serving map tiles with ultra-low latency (<50ms). Second, ingesting massive amounts of GPS telemetry to compute real-time traffic and update navigation routes. Given 1B users driving roughly 35 minutes a week, batching GPS every 30 seconds results in over 10 billion events a day, or a peak of 1 million QPS. Standard databases will buckle under this write load."

## 2. Map Tile Serving
> Say: "For rendering, we cannot serve static PNGs. We must use Vector Tiles compressed as Protobufs. This reduces payload size from 20KB to 5KB per tile, saving petabytes of bandwidth, and shifts the rendering workload to the client's GPU. The globe is partitioned using a QuadTree. We precompute these tiles across 21 zoom levels, store them in S3, and serve them heavily cached via a global CDN. This ensures our <50ms read latency."

## 3. Telemetry & Live Traffic
> Say: "For the 1M peak QPS telemetry write path, we must decouple the clients from our databases. Mobile clients will batch GPS coordinates and push them to an API Gateway, which dumps them directly into Apache Kafka. From Kafka, a stream processing engine like Apache Flink will read the events. Flink performs 'map matching'—using algorithms like Hidden Markov Models to snap noisy GPS data to actual road graph edges. It then aggregates average speeds per segment and writes these live traffic updates to our In-Memory Route Graph Cache. Raw telemetry is flushed to Cassandra for offline analysis."

## 4. Routing & Precomputation
> Say: "Standard Dijkstra's algorithm is $O(V \log V + E)$, which is too slow to calculate a route from New York to LA on a graph with millions of nodes. Instead, we use hierarchical routing, specifically Contraction Hierarchies (CH). We use a massive offline MapReduce pipeline to precompute 'shortcuts' across major highways. At runtime, the Route Service queries the In-Memory Graph Cache and only needs to traverse local roads until it hits a precomputed highway shortcut, dropping route calculation latency to under 5ms."

## 5. Rerouting (The Loop)
> Say: "Finally, the system is a closed loop. Active navigation sessions are stored in a fast cache like Redis. When Flink detects a severe traffic penalty on an edge, it notifies the Reroute Service. The service checks Redis for any users currently routed over that edge, recalculates their ETA, and if a faster path exists, pushes a new route via WebSocket or Server-Sent Events to the client."
