# Google Maps & Navigation - Interview Scoring Rubric

## Scoring rubric

| Dimension | Weight | Strong signal |
|---|---|---|
| Requirements & Constraints | 15% | Correctly identifies the duality of the problem (static map tiles vs. dynamic routing/telemetry). Sizes storage for tiles and QPS for telemetry accurately. |
| Map Serving Architecture | 20% | Recommends Vector tiles over Raster. Articulates the QuadTree zoom level structure and appropriately places a CDN in front of object storage (S3). |
| Routing Algorithm | 25% | Recognizes Dijkstra is too slow for global routing. Suggests hierarchical routing (e.g., Contraction Hierarchies or A* on partitions) and offline precomputation. |
| Telemetry Ingestion | 20% | Designs a robust write path (Client Batching -> Gateway -> Kafka -> Flink -> Cassandra) capable of handling 1M peak QPS without bottlenecking. |
| Traffic & Rerouting | 10% | Explains map-matching (snapping GPS to edges) and how stream processors aggregate live speeds to update the in-memory route graph, triggering active session reroutes. |
| Trade-offs & Depth | 10% | Deeply understands the client vs. server processing trade-offs (e.g., battery life vs. data freshness, vector rendering). |

## Performance bands

- **1-2 (Weak):** Proposes a monolithic DB for routing and telemetry. Uses Raster PNGs without considering bandwidth. Suggests standard Dijkstra for routing. Fails to decouple ingestion from processing.
- **3 (Okay):** Separates tiles and routing. Mentions CDNs. Uses Kafka for ingestion. Might struggle to explain map-matching or how hierarchical routing speeds up graph traversal.
- **4 (Solid):** Strong architecture. Justifies Vector tiles. Designs a scalable Flink/Kafka pipeline. Explains how live traffic updates the route graph.
- **5 (Strong):** Exceptionally clear on Contraction Hierarchies and offline precomputation. Nuanced understanding of map-matching algorithms (e.g., Hidden Markov Models). Perfectly sizes the system and explicitly discusses client-side batching trade-offs.

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [DESIGN.md](./DESIGN.md)
