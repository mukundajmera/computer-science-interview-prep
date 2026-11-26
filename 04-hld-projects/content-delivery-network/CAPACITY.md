# Back-of-Envelope Estimation (Only What Changes Design)

## Traffic

| Metric | Value | Formula |
|---|---|---|
| DAU | 1 Billion | scenario assumption |
| Requests/user/day | 50 | scenario assumption |
| Daily requests | 50 Billion | 1B × 50 |
| Avg QPS | ~580,000 | 50B / 86400 |
| Peak QPS | ~1.16 Million | avg × 2 (burst factor) |

## Storage / Bandwidth

| Data Type | Avg Size | Bandwidth | Capacity Notes |
|---|---|---|---|
| Mixed Assets (Images to Video) | 1 MB | ~4.6 Tbps Avg (580k * 1MB * 8) | Needs NVMe SSDs for tiering |
| Edge Nodes | N/A | Peak 100 Tbps total | 10,000 nodes across 500 PoPs |

## Decision Notes
- **Which estimate forces a design choice?** The peak bandwidth of 100 Tbps and 1MB average asset size dictate that we cannot store everything in RAM. We must use tiered storage at the edge (RAM for hot metadata/small assets, NVMe SSDs for chunks/large files).
- **What assumption is most uncertain?** The cache hit ratio (90%). If it drops to 70% during a cache invalidation event, the 1.16M peak QPS will result in ~348,000 QPS hitting the Origin Shield, making request coalescing absolutely critical.
