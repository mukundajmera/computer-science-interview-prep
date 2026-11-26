# Google Maps & Navigation - Approach & Strategy

## 1. Deconstruct the Problem

A global navigation system like Google Maps encompasses two vastly different workloads:
1. **Static/Semi-Static Read-Heavy Workload:** Serving map data visually to clients.
2. **Highly Dynamic Read/Write Workload:** Real-time location telemetry, traffic aggregation, and route calculation.

The strategy must cleanly decouple map rendering from real-time routing.

## 2. Address Map Tile Delivery
- Serving the entire map as a single file is impossible. The world is divided into a grid (QuadTree) at various zoom levels (0-21).
- We must shift from legacy raster images (PNGs) to vector graphics (Protobufs). This is the key insight for reducing bandwidth from 20KB down to 5KB per tile, pushing rendering to the client's GPU.
- Content Delivery Networks (CDNs) are mandatory here. The 70 PB of precomputed tiles sit in S3, heavily cached at the edge.

## 3. Solve the Navigation Bottleneck
- Finding the shortest path on a graph representing the global road network using standard Dijkstra's algorithm is too slow ($O(V \log V + E)$).
- **Strategy:** Hierarchical routing. Use algorithms like Contraction Hierarchies (CH) or A* with landmarks. We precompute "shortcuts" for major highways offline so that the online query only traverses local roads to the nearest highway, then jumps across the shortcut.

## 4. Master Real-Time Traffic Telemetry
- 1B DAU generating GPS signals every 15-30 seconds results in massive write throughput (~1M peak QPS).
- **Strategy:** Decouple ingestion from processing.
    - Mobile clients batch GPS signals locally to save battery and network connections.
    - An API Gateway feeds a high-throughput message queue (Kafka).
    - Stream processing (Flink) reads the stream, performs "map matching" (snapping noisy GPS coordinates to actual road graph edges), and computes real-time segment speeds.
- Store raw telemetry in a write-optimized store like Cassandra. Store active routing states in Redis to quickly trigger reroutes if the ETA degrades.

## 5. Summary of Key Themes
- **Precomputation:** Vector tile generation and Contraction Hierarchies happen offline.
- **Client-Side Heavy Lifting:** GPU rendering and GPS batching.
- **Stream Aggregation:** Converting raw GPS streams into actionable live traffic speeds.
