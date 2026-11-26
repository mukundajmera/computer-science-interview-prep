# Proximity Service - Follow-Up Questions

## Follow-up questions

1. **What changes at 10x scale (e.g., 2 billion businesses)?**
   - The index size grows to ~32GB. While it still fits on a large server, a single Redis node might struggle with CPU bottlenecks at 250,000 QPS. We would need to shard the Redis cluster, hashing by Geohash, so different geographical areas are served by different Redis shards.

2. **How do you handle a regional outage (e.g., AWS us-east-1 goes down)?**
   - Proximity services are highly regional. Users in New York care about New York data. We would run active-active deployments in multiple regions (e.g., US East and US West). User traffic is routed via GeoDNS. If a region fails, traffic fails over. The underlying databases must use cross-region replication.

3. **How do you handle highly dense areas (e.g., Manhattan) where a Geohash cell might return thousands of businesses?**
   - We can dynamically adjust the Geohash precision. If a length-6 Geohash has too many entities, we can use a length-7 Geohash for that specific area. Alternatively, we enforce a strict pagination limit and only calculate exact distances for the top $N$ closest businesses.

4. **How do you filter results (e.g., "Open Now", "Highly Rated") along with distance?**
   - Pure Geohash in Redis struggles with complex secondary filtering. At this stage, we would likely migrate from Redis to a dedicated search engine like Elasticsearch or Apache Solr, which natively supports combining geospatial queries with text and attribute filtering.

## Variants and extensions
- **Moving targets:** What if businesses are moving (e.g., a ride-sharing service like Uber)? The write path becomes hyper-active. Geohash in Redis might suffer from write contention. A custom in-memory grid or QuadTree specifically designed for high-frequency updates might be required.
- **Offline mode:** How to support users without internet? Download regional Geohash data directly to the client device on Wi-Fi and perform local SQLite queries.

## Interviewer probes to prepare
- "Walk me through exactly how you query the 9 cells."
- "What happens if the Redis cache is completely wiped out?"
- "How do you calculate the exact distance after fetching the IDs from the Geohash?" (Answer: Haversine formula on the stateless app tier).

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design Document](DESIGN.md)
