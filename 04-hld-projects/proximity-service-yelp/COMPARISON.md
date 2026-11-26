# Proximity Service - Comparison of Geospatial Indexing

## Indexing Strategies

| Concern | Geohash (Redis/KV) | QuadTree (In-Memory) | PostGIS (Relational) | Elasticsearch (Lucene) |
|---|---|---|---|---|
| **Mechanism** | 1D string prefix mapping | 2D tree subdivision | R-Tree / GiST index | BKD trees |
| **Read Latency** | Ultra-low (< 5ms) | Ultra-low (< 5ms) | Medium (10-50ms) | Low-Medium (10-30ms) |
| **Write Complexity** | Simple (String update) | Complex (Tree rebalancing) | Moderate | Moderate (Segment merges) |
| **Density Handling** | Fixed grid sizes | Dynamic grid sizes | Dynamic | Dynamic |
| **Horizontal Scaling**| Trivial (Hash by prefix) | Difficult (Custom sharding) | Difficult (DB Sharding) | Native (Index sharding) |
| **Filtering (Text)** | Poor | Poor | Excellent (SQL) | Excellent (Lucene) |
| **Best For** | Yelp, basic proximity | Uber, highly dynamic points | Enterprise GIS apps | Complex search apps |

## Key Differences & Migration Path

- **Phase 1 (Startups):** Often begin with PostGIS. It's built into PostgreSQL, handles basic scale well, and allows complex SQL joins on business metadata.
- **Phase 2 (Scale):** Move to Geohash + Redis. Once read traffic spikes and the system becomes globally distributed, caching Geohashes in Redis provides massive read throughput.
- **Phase 3 (Feature Rich):** Move to Elasticsearch. When product requirements demand complex filtering (e.g., "Find coffee shops, rated 4+, open now, within 2 miles"), Elasticsearch provides the best balance of text search and geospatial capabilities natively.

## Cross-links
- [Approach](APPROACH.md)
- [Design Document](DESIGN.md)
