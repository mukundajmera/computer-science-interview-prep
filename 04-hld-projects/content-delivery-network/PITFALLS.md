# CDN HLD Interview Pitfalls

## 1. Missing Request Coalescing
The most common failure is designing a system where every cache miss at the edge directly hits the customer origin. In a 0% cache hit scenario during a global purge, 10,000 edge nodes fetching the same asset will instantly crash the customer origin (Thundering Herd). **Correction**: Introduce a Regional Origin Shield with a Request Coalescer that collapses concurrent requests into a single fetch.

## 2. Infeasible Pure-RAM Caching
Candidates often suggest caching all content in Redis or Memcached. With a peak bandwidth of 100 Tbps and massive asset libraries (e.g., video chunks), RAM is prohibitively expensive and small. **Correction**: Propose Tiered Storage at the edge: Hot metadata and small assets in RAM, larger chunks in NVMe SSDs.

## 3. Misunderstanding Anycast Limitations
Candidates often propose pure Anycast for routing, assuming it solves all load balancing problems. Anycast routes based on BGP topological distance, not server load. If a PoP is CPU-bound, Anycast will still send traffic there. **Correction**: Acknowledge Anycast's limitations and propose a hybrid model using GeoDNS for load-aware traffic steering.

## 4. Unrealistic Global Purge via DB Polling
Designing the global cache purge mechanism using a relational database where 10,000 edge nodes poll for updates every second. This introduces massive DB load and fails the <150ms latency SLA. **Correction**: Use a push-based multi-tier Pub/Sub system (e.g., Redis) for immediate fan-out.
