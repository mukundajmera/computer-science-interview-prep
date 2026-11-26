# Proximity Service - Problem Statement

## Core User Value
Design a proximity service (similar to Yelp or Google Places) that allows users to discover nearby businesses based on their current location and provides business owners the ability to manage their profiles.

## Functional Requirements
- Search nearby places within radius R (e.g. 5km) around a given `(latitude, longitude)`.
- Add/update business profile (business owners can perform CRUD operations on their business profiles).
- Filter by category/rating.
- Users can look up detailed information for a specific business by its ID.
- Search results should be sorted by distance from the user's location.

## Non-Functional Requirements
- **Latency:** P99 < 100ms for radius search queries.
- **Scale:**
  - 100M Daily Active Users (DAU).
  - 200M total businesses registered.
  - 20,000 Search QPS.
  - 200 Write QPS.
- **Read/Write Ratio:** Read-heavy (100:1 read/write ratio).
- **Availability:** 99.99% uptime.
- **Caching:** geo-distributed caching.
- **Consistency:** Eventual consistency is acceptable for business profile updates, but searches must be fast and highly available.

## Constraints & Out of Scope
- Navigation and routing (turn-by-turn directions) are out of scope.
- We focus primarily on the geospatial indexing and retrieval mechanics.
