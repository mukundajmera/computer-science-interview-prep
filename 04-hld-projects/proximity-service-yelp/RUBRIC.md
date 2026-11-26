# Proximity Service - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|---|---|---|
| Problem Scoping | 15% | Explicitly defines radius boundaries (500m-20km) and clarifies read-heavy vs write-light traffic. |
| Geospatial Understanding | 35% | Clearly articulates trade-offs between Geohash, QuadTree, and 2D SQL. Chooses a mechanism that fits the scale. |
| Scale & Capacity Planning | 20% | Correctly identifies that the entire index (3.2GB) can fit in memory and models the design around this realization. |
| Edge Case Handling | 15% | Addresses boundary issues (querying neighboring geohashes) and dense vs sparse population zones. |
| API & Data Modeling | 15% | Defines clear database schemas and efficient caching mechanisms for business profiles. |

## Performance bands

- **Weak (1-2):** Tries to use raw SQL for 2D geospatial queries. Fails to understand the scale difference between the index and the raw profile data.
- **Okay (3-4):** Suggests Geohash or QuadTree but struggles to explain how to handle edge cases (e.g., businesses just outside the cell boundary). Overcomplicates the architecture.
- **Strong (5):** Quickly realizes the index fits in memory, selects Geohash for simple horizontal scaling in Redis, clearly explains the 9-cell search logic, and handles eventual consistency for writes seamlessly.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design Document](DESIGN.md)
