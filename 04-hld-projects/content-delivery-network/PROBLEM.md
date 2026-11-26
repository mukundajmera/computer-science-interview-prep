# Content Delivery Network (CDN) System

## Problem Statement

Design a Content Delivery Network (CDN) that accelerates web content delivery, particularly focusing on Edge Caching and Media Delivery (such as large videos). The system needs to efficiently route users to the nearest Edge Point of Presence (PoP), cache static and dynamic content, minimize origin fetches through coalescing, and support near-realtime global cache purging.

---

## Requirements and Constraints

### Functional Requirements

1. Route users to the nearest/optimal Edge PoP.
2. Cache static media (images, large videos) and dynamic assets using standard headers (`Cache-Control`, `ETag`).
3. Support range request caching for large videos.
4. Support fast global cache purge fan-out.
5. Provide a 2-tier caching hierarchy (Edge PoP -> Regional Origin Shield -> Customer Origin Server) to protect origin servers.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Latency (Cache Hit) | < 50 ms P99 |
| Cache Purge Latency | < 150 ms to 10,000 edge nodes globally |
| Availability | 99.99% |
| Durability | Caches are transient; authoritative data remains at the Origin |
| Cache Hit Ratio | > 90% at Edge |
| Origin Coalescing | Collapse 100 concurrent requests for the same asset into 1 origin fetch |

### Capacity Assumptions

- 1 Billion DAU.
- Average asset size: 1 MB (mixed workload: 10KB images to 500MB videos).
- Users request 50 assets per day on average.
- Network bandwidth peak: 100 Tbps globally.
- Total Edge PoPs: 500.
- Nodes per PoP: 20 (Total Edge nodes: 10,000).

### Constraints
- Must handle temporary network partitions without crashing.
- Purge must propagate securely and reliably.

### Out of Scope

- Detailed DNS infrastructure design beyond the routing mechanisms (Anycast/GeoDNS).
- Detailed edge compute platform logic (serverless functions at edge).
- Analytics and billing pipelines.

---
