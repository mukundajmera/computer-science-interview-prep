# CDN HLD Interview Pitfalls

## 1. Missing Request Coalescing
The most common failure is designing a system where every cache miss at the edge directly hits the customer origin. In a 0% cache hit scenario during a global purge, 10,000 edge nodes fetching the same asset will instantly crash the customer origin (Thundering Herd). **Correction**: Introduce a Regional Origin Shield with a Request Coalescer that collapses concurrent requests into a single fetch.

## 2. Infeasible Pure-RAM Caching
Candidates often suggest caching all content in Redis or Memcached. With a peak bandwidth of 100 Tbps and massive asset libraries (e.g., video chunks), RAM is prohibitively expensive and small. **Correction**: Propose Tiered Storage at the edge: Hot metadata and small assets in RAM, larger chunks in NVMe SSDs.

## 3. Misunderstanding Anycast Limitations
Candidates often propose pure Anycast for routing, assuming it solves all load balancing problems. Anycast routes based on BGP topological distance, not server load. If a PoP is CPU-bound, Anycast will still send traffic there. **Correction**: Acknowledge Anycast's limitations and propose a hybrid model using GeoDNS for load-aware traffic steering.

## 4. Unrealistic Global Purge via DB Polling
Designing the global cache purge mechanism using a relational database where 10,000 edge nodes poll for updates every second. This introduces massive DB load and fails the <150ms latency SLA. **Correction**: Use a push-based multi-tier Pub/Sub system (e.g., Redis) for immediate fan-out.

## 5. Caching Full Multi-Gigabyte Media Files as Monolithic Objects
Fetching and caching an entire 10 GB video when a viewer only requests `bytes=0-1048575` wastes origin bandwidth, fills NVMe capacity, and spikes time-to-first-byte. **Correction**: Split large media into fixed-size chunks (such as 2 MB segments) keyed per chunk so edge nodes fetch and coalesce only the missing byte ranges.

## 6. Ignoring Cache-Key Normalization and Query-String Cache Busting
Keying edge caches on raw URLs lets malicious or misconfigured clients append random query parameters to bypass the >90% cache hit ratio and flood the customer origin. **Correction**: Normalize cache keys by stripping non-whitelisted query parameters and hashing `Customer_ID + normalized_URL` consistently across PoP nodes.

## 7. Treating Origin Outages or Shield Partitions as Immediate 5xx Failures
Failing every edge request the moment a customer origin times out or a PoP loses connectivity to the Origin Shield breaks the 99.99% availability target and drops in-flight purge visibility. **Correction**: Honor `Stale-While-Revalidate` and stale-on-error policies while the origin is unreachable, and fall back to short TTLs plus purge-log resynchronization when a partitioned PoP reconnects.

## 8. Performing Synchronous Disk Deletes During Global Cache Purges
Blocking the edge purge daemon on physical NVMe deletions across 10,000 nodes causes purge fan-out latency to breach the <150 ms global SLA. **Correction**: Apply an immediate logical tombstone in RAM upon receiving the Pub/Sub purge event to block stale reads, then reclaim SSD blocks asynchronously in the background.

---

## Quick Self-Check

- Did I include a Regional Origin Shield with request coalescing to prevent origin thundering herds?
- Did I use tiered RAM + NVMe SSD edge storage instead of pure-RAM caching?
- Did I pair Anycast BGP with GeoDNS for load-aware traffic steering?
- Did I design a push-based multi-tier Pub/Sub tree for <150 ms global purges instead of DB polling?
- Did I chunk large media assets for HTTP Range request caching?
- Did I normalize cache keys to prevent random query-string cache busting?
- Did I define stale-serving and reconnect purge-sync fallbacks for origin outages and PoP partitions?
- Did I use in-RAM tombstones with async SSD cleanup during cache purges?
