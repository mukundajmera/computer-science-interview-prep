# CDN HLD Interview Rubric

## 1. Requirements and Constraints (Core Design Contract)
- **Strong**: Explicitly notes that 1MB average asset size and peak 100 Tbps bandwidth forces a tiered storage approach (RAM + NVMe SSDs). Identifies the critical need for a request coalescer to handle cache stampedes.
- **Weak**: Misses tiered storage necessity or treats the system as fitting entirely in RAM. Fails to mention cache purge SLA.

## 2. Core Architecture and APIs
- **Strong**: Articulates a clear 2-tier cache hierarchy (Edge PoP -> Regional Origin Shield -> Origin) with `GET /asset` and `POST /purge`. 
- **Weak**: Single tier cache that overwhelms the customer origin on cache misses, or lacks explicit purge mechanism.

## 3. Deep Dive: Routing (Anycast vs GeoDNS)
- **Strong**: Proposes a Hybrid Anycast + GeoDNS approach, explicitly defining the trade-off: Anycast for raw speed and default routing, GeoDNS for granular load shedding when a PoP is overwhelmed.
- **Weak**: Hand-waves routing with "just use Route 53" without understanding the mechanics of Anycast BGP.

## 4. Deep Dive: Fast Cache Purge
- **Strong**: Specifies a TCP-based multi-level Pub/Sub tree (e.g., Redis or Kafka) to achieve <150ms global invalidation across 10k nodes, avoiding unreliable UDP broadcasts or slow DB polling.
- **Weak**: Suggests database polling which adds unacceptable latency, or UDP without handling message drops.

## 5. Failure Traces & Explicit Verification
- **Strong**: Maps at least one explicit failure trace, e.g., Network Partition between Edge PoP and Shield resulting in reliance on local TTLs, or Origin down triggering `Stale-While-Revalidate`.
- **Weak**: Only covers the happy path cache hit; ignores origin downtime or network partitions.
