# Proximity Service - Common Pitfalls

## 1. Falling back to Naive 2D SQL
- **Signal:** Candidate suggests `SELECT * WHERE lat BETWEEN x AND y AND long BETWEEN a AND b`.
- **Root Cause:** Lack of familiarity with geospatial indexing and the limitations of B-trees on multi-dimensional data.
- **Mitigation:** Gently prompt the candidate on how the database would execute this query under the hood (table scan).
- **Validation:** Check if they pivot to 1D indexing strategies like Geohash or QuadTree.

## 2. Overcomplicating the Data Store
- **Signal:** Designing a complex, horizontally sharded, custom-built QuadTree service from scratch for initial scale.
- **Root Cause:** Missing the capacity calculation that the entire index is only ~3.2GB.
- **Mitigation:** Ask the candidate to calculate the total size of the index (business ID + location representation).
- **Validation:** Candidate realizes it fits in a single Redis node's memory and simplifies the architecture.

## 3. Ignoring the Boundary Problem
- **Signal:** Candidate uses Geohash but only queries the single Geohash cell the user is currently standing in.
- **Root Cause:** Not visualizing the grid system and how a user might be 5 meters away from a business that happens to fall in the adjacent cell.
- **Mitigation:** Draw a grid. Put the user on the line between two cells and the business just across the line. Ask how the system finds it.
- **Validation:** Candidate proposes fetching the central cell and its 8 surrounding neighbors.

## 4. Strong Consistency on the Write Path
- **Signal:** Adding distributed locks or two-phase commits to ensure a business profile update is instantly available in the search index globally.
- **Root Cause:** Misunderstanding the user value; users don't need real-time updates for a restaurant changing its hours.
- **Mitigation:** Ask about the required SLA for write consistency.
- **Validation:** Candidate pivots to an asynchronous, eventually consistent update pipeline (e.g., via Kafka).

## Cross-links
- [Rubric](RUBRIC.md)
- [Design Document](DESIGN.md)
