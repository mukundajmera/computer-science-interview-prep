# CDN Alternative Architectures

## Alternative 1: Pure Anycast Routing (No GeoDNS)
- **Design:** All PoPs broadcast the exact same Anycast IP space. BGP handles 100% of routing.
- **Pros:** Utterly simple DNS setup. Lowest possible latency to the topologically nearest node. Excellent for DDoS mitigation (traffic naturally distributes globally).
- **Cons:** **No Load Shedding.** BGP does not know about CPU utilization or Disk I/O. If a specific PoP is overloaded (e.g., a massive event in one city), Anycast will stubbornly route users into a congested, failing PoP. 
- **Verdict:** Rejected for this design in favor of a Hybrid Anycast + GeoDNS approach, which allows us to withdraw Anycast routes dynamically or use DNS to steer traffic away from hot spots.

## Alternative 2: Database Polling for Cache Purge
- **Design:** Instead of a Redis Pub/Sub push model, edge nodes query a centralized database (e.g., Cassandra or CockroachDB) every 5 seconds to see if any of their cached keys have been purged.
- **Pros:** Highly durable. No dropped messages during network partitions. Simpler architecture.
- **Cons:** **Massive Polling Load & Latency.** 10,000 edge nodes polling the DB continuously wastes immense resources. More importantly, it completely fails the <150ms global purge SLA, as a 5-second polling interval guarantees multi-second staleness.
- **Verdict:** Rejected. The <150ms latency requirement strictly mandates a push-based multi-tier Pub/Sub tree.

## Alternative 3: Flat Cache Architecture (No Origin Shield)
- **Design:** Edge PoPs on cache misses reach out directly to the Customer Origin.
- **Pros:** Cheaper infrastructure. One less hop on a cache miss (lower latency for misses).
- **Cons:** **Thundering Herd / Cache Stampede.** If a highly popular asset is purged or expires, 10,000 edge nodes will simultaneously fetch it from the Customer Origin. This will instantly crash almost any origin server.
- **Verdict:** Rejected. A Tier-2 Regional Origin Shield with a Request Coalescer is absolutely mandatory to protect customer infrastructure and provide high cache hit ratios.
