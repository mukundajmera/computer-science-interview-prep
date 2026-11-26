# Content Delivery Network - Strong Answer

## 1. Requirements & Core Constraints (0-5 minutes)
"I'll design a Content Delivery Network focused on edge caching and media delivery.
My primary goals are ultra-low latency reads (<50ms P99), high availability (99.99%), and protecting the customer's origin server from traffic spikes.
For estimates, assuming 1 Billion DAU fetching 50 assets a day, we're looking at ~580,000 avg QPS and 1.16M peak QPS. Assuming a 1MB average asset size, peak bandwidth is around 100 Tbps.
**Key Design Driver:** This 100 Tbps bandwidth and 1MB size means we cannot store everything in RAM. We must use Tiered Storage (RAM + NVMe SSDs). Furthermore, if a popular asset expires, 1.16M QPS hitting the origin will crash it, making Request Coalescing mandatory."

## 2. APIs & Data Model (5-10 minutes)
"The system exposes standard HTTP endpoints for asset fetching, respecting headers like `Range`, `Cache-Control`, and `Stale-While-Revalidate`. 
For the control plane, we need a fast invalidation API: `POST /purge` taking a URL pattern.
Data will be stored on Edge Nodes using Consistent Hashing on `hash(CustomerID + AssetURL)` to partition assets across specific servers/disks within a PoP."

## 3. High-Level Architecture (10-20 minutes)
"I propose a 2-Tier Architecture:
1. **Edge PoP**: Geographically distributed clusters (e.g., 500 globally). Clients are routed here via a hybrid of Anycast (for raw BGP speed) and GeoDNS (for load-shedding away from hot PoPs).
2. **Regional Origin Shield**: An intermediate cache tier (e.g., 10 globally) sitting between the Edge PoPs and the Customer Origin.

**Read Path:** Client hits Edge Node. If Cache Hit, return from RAM/SSD.
**Write Path (Cache Fill):** On Cache Miss, Edge Node asks Origin Shield. If Shield misses, it asks Customer Origin. Crucially, the Shield implements a **Request Coalescer**: if 100 edge nodes ask for the same asset, it holds 99 connections, makes 1 fetch to the Origin, and multiplexes the response back.

**Purge Path:** A `POST /purge` hits the Control Plane, which pushes the invalidation message down a multi-level Redis Pub/Sub tree (Global -> Regional -> PoP) to achieve <150ms fan-out without database polling latency."

## 4. Deep Dives & Trade-offs (20-35 minutes)
"Let's dive into **Routing Trade-offs**. Pure Anycast is fastest but routing is strictly based on BGP topological distance. If an Edge PoP's CPUs are maxed out, Anycast will still route traffic there. Therefore, I chose a Hybrid model: Anycast provides the default fast IPs, but if a PoP degrades, our health checkers update GeoDNS to steer new DNS resolutions to the next closest Anycast IP block.

Next, **Media Delivery & Range Caching**. To efficiently cache a 10GB video, the Edge Node chunks it into 2MB blocks. A client request for `bytes=0-5000000` is translated into cache keys `vid_chunk0`, `vid_chunk1`, `vid_chunk2`. This prevents us from having to fetch or store the entire 10GB file just to serve the first 10 seconds.

Finally, **Failure Trace: Network Partition**. If an Edge PoP loses connection to the Origin Shield, two things happen: 
1. Cache misses fail (returning 502/504 to the client).
2. Purge Pub/Sub messages are dropped. To mitigate serving permanently stale data, the Edge Node must rely on strict TTLs and upon reconnection, sync a transaction log or aggressively evict older data."

## 5. Wrap-up (35-45 minutes)
"In summary, we built a 2-tier CDN using Tiered RAM/SSD storage to handle 100 Tbps bandwidth. We protected the Customer Origin using Request Coalescing at the Origin Shield, and achieved sub-150ms cache invalidations using a Redis Pub/Sub fan-out tree. The system gracefully handles origin downtime via `Stale-While-Revalidate` and utilizes chunking for massive media files."
