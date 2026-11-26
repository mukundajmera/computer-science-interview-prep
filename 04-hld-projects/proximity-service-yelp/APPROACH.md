# Proximity Service - Approach & Trade-offs

## Geospatial Indexing Strategies

The core challenge of a proximity service is efficiently querying two-dimensional coordinates (latitude, longitude) to find points within a specific radius.

### 1. 2D SQL Queries (Naive Approach)
```sql
SELECT * FROM businesses 
WHERE lat BETWEEN min_lat AND max_lat 
  AND long BETWEEN min_long AND max_long;
```
- **Pros:** Simple to implement using standard relational databases.
- **Cons:** Standard B-tree indexes cannot efficiently index two dimensions simultaneously. The database will likely perform a table scan or index scan on one dimension, leading to severe performance bottlenecks at scale.

### 2. Geohash
Geohash encodes 2D coordinates into a 1D string (using a Base32 Morton curve). The length of the string determines the precision (e.g., length 6 maps to a grid roughly $\pm 610$ m).
- **Pros:** 
  - Simple 1D string matching.
  - Scales easily horizontally (e.g., simple string keys in a distributed cache or NoSQL database).
  - Perfect for finding businesses in the same or neighboring grids.
- **Cons:** 
  - Edge cases where businesses are physically close but in different Geohash cells (boundary misses). This is resolved by querying the center cell plus its 8 immediate neighbor cells.
  - Cell sizes are fixed, meaning dense urban areas will have many more businesses per cell than rural areas.

### 3. QuadTree
A QuadTree recursively subdivides 2D space into four quadrants until each quadrant (leaf node) contains a threshold number of points (e.g., 100 businesses).
- **Pros:**
  - Adapts to variable density. Dense areas have deeper trees (smaller cells); rural areas have shallower trees (larger cells).
  - Excellent for $k$-nearest neighbor queries.
- **Cons:**
  - Complex dynamic rebalancing when businesses are added/updated.
  - Often implemented entirely in-memory, requiring long cold start times to rebuild the tree upon server restart.
  - Harder to partition and distribute across multiple servers compared to Geohash.

### 4. Google S2 Geometry
Maps the sphere to a 1D Hilbert curve, generating 64-bit integers.
- **Pros:** Highly accurate on a spherical Earth, fast, and mathematically rigorous.
- **Cons:** More complex to implement and debug than Geohash.

### Decision
**Geohash** backed by Redis sets is chosen for its simplicity, horizontal scalability, and efficient caching. It easily handles our read-heavy workload and 50ms latency requirement.

## Back-of-the-Envelope Calculations

- **Traffic:**
  - $100\text{M DAU} \times 5\text{ searches/day} = 500\text{M searches/day}$
  - $\text{Avg QPS} = \frac{500\text{M}}{86,400} \approx 5,787 \approx 5,000\text{ QPS}$
  - $\text{Peak QPS} = 5 \times 5,000 = 25,000\text{ QPS}$

- **Storage:**
  - Business profiles: $200\text{M} \times 2.5\text{ KB} = 500\text{ GB}$
  - Geohash index: 6-char geohash + 8-byte `business_id` $\approx 16\text{ bytes} \times 200\text{M} \approx 3.2\text{ GB}$.
  - The entire geospatial index fits comfortably in the RAM of a single Redis node, though we will distribute it for fault tolerance and throughput.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Design Document](DESIGN.md)
