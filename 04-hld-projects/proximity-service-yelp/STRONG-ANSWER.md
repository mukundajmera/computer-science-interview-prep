# Proximity Service - Strong Answer Guide

A strong candidate drives the interview proactively, focusing on the intersection of data structures (geospatial indexing) and distributed systems (caching and availability).

## 1. Quick Requirements & Math
**Strong Signal:** The candidate doesn't get bogged down in math. They quickly realize:
> **Say:** "We have 200 million businesses. A 6-character Geohash plus an 8-byte ID is about 14 bytes. Multiply by 200 million, and the entire search index is under 4GB. This means we don't need a complex distributed database for the search path; we can cache the entire world's map in memory on a single Redis node (replicated for high availability)."

## 2. Decisive Indexing Strategy
**Strong Signal:** The candidate explicitly compares QuadTree and Geohash.
> **Say:** "While QuadTrees are great for varying densities (like dense cities vs. rural areas), they are complex to distribute and rebalance on updates. Given our read-heavy workload and static business locations, Geohash provides a much simpler distributed model. We can treat Geohashes as standard strings and shard them across a Redis cluster using simple hash slots."

## 3. Addressing the Edge Case
**Strong Signal:** The candidate immediately brings up the boundary problem without being prompted.
> **Say:** "The flaw with Geohash is that a user standing on the border of a cell might miss a business 10 feet away in the adjacent cell. To solve this, the search service will calculate the user's Geohash and its 8 neighboring cells. We query Redis for all 9 cells. Since Redis handles set unions efficiently, this is a very fast operation."

## 4. Clear Separation of Write and Read Paths
**Strong Signal:** The candidate decouples the persistent storage from the search index.
> **Say:** "Business owners expect their profile updates to be durable, but users don't need to see a restaurant's new hours the millisecond they are changed. We will use a standard relational DB (PostgreSQL) as the source of truth for business CRUD operations. An asynchronous pipeline (e.g., CDC or Kafka) will propagate these changes to the Redis Geohash index and profile cache, achieving eventual consistency and keeping the write path separate from the critical read path."

## 5. Final Polish (Distance Calculation)
**Strong Signal:** The candidate explains exactly where distance is calculated.
> **Say:** "Geohash gives us a rough bounding box. Once we get the list of business IDs and their exact coordinates from Redis, the stateless search application servers will use the Haversine formula to compute the exact distance to the user, sort the results, and truncate to the requested page size before returning to the client."

## Cross-links
- [Rubric](RUBRIC.md)
- [Design Document](DESIGN.md)
