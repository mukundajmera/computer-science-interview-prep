# Google Maps & Navigation - Comparison

## Cross-links
- [PROBLEM.md](./PROBLEM.md)
- [APPROACH.md](./APPROACH.md)
- [DESIGN.md](./DESIGN.md)

## Map Rendering Delivery

| Concern | Raster Tiles (PNG) | Vector Tiles (Protobuf) |
|---|---|---|
| **Bandwidth** | High (~20KB/tile) | Low (~5KB/tile) |
| **Rendering compute** | Server-side | Client-side (GPU) |
| **Rotation / 3D** | Poor (text rotates with image) | Excellent (text remains upright) |
| **Styling** | Requires new images for night/day | Client applies CSS-like styles dynamically |
| **Storage** | Extremely high | Moderate |

## Global Routing Algorithms

| Concern | Standard Dijkstra | A* Search | Contraction Hierarchies (CH) |
|---|---|---|---|
| **Query Speed** | Very Slow (Seconds/Minutes) | Slow (Seconds) | Extremely Fast (< 5ms) |
| **Precomputation** | None | Minor (Heuristics) | Heavy (Days of offline processing) |
| **Space Complexity**| Low | Low | High (Shortcut edges stored) |
| **Live Traffic Updates**| Trivial (Just change edge weight) | Easy | Hard (Requires specialized variants like CRP) |

## Telemetry Storage

| Concern | PostgreSQL / MySQL | Apache Cassandra |
|---|---|---|
| **Write Throughput** | Bottlenecks at high scale without complex sharding | Exceptionally high (LSM-tree architecture) |
| **Time-Series Suitability**| Low | High (Wide-column, clustering by timestamp) |
| **Consistency** | Strong (ACID) | Eventual / Tunable |
| **Use Case in Maps** | User profiles, billing | Raw GPS telemetry ingestion |
