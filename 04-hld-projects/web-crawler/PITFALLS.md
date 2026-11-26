# Web Crawler — Common Pitfalls

1. Ignoring `robots.txt` and per-host politeness constraints.
2. Single global queue without host sharding, causing hot-domain starvation.
3. URL dedup based on raw strings without normalization/canonicalization.
4. Infinite retries on transient failures, amplifying load on failing hosts.
5. No content fingerprinting, storing near-duplicate pages repeatedly.
6. Tight coupling of fetch and parse paths, reducing fault isolation.

## How to avoid them
- Use a host-aware frontier scheduler and enforce token-bucket limits per host.
- Normalize URLs before dedup and maintain fingerprint indices.
- Track retry reason codes to separate transient from terminal failures.
