# Performance Numbers (Back-of-the-Envelope)

Use these as interview-grade ranges for reasoning, not fixed guarantees.

## Latency quick reference

| Operation | Typical latency range |
|---|---|
| L1 cache reference | ~0.5 ns |
| L2 cache reference | ~3 ns |
| Main memory | ~100 ns |
| SSD random read | ~50-150 us |
| NVMe write | ~10-50 us |
| HDD seek | ~2-10 ms |
| Intra-DC round trip | ~0.3-1 ms |
| Cross-region RTT | ~50-200 ms |
| Redis/Memcached read | ~0.5-2 ms |
| Relational DB read (cached) | ~1-5 ms |
| Relational DB read (disk) | ~5-30 ms |

---

## Practical throughput ranges (order-of-magnitude)

| Component | Typical range |
|---|---|
| In-memory cache node | 100k-200k+ ops/sec |
| Single app server (optimized I/O) | 10k-100k+ concurrent connections |
| Single relational primary (well-tuned simple workload) | 10k-20k+ writes/sec |
| Message broker node (workload dependent) | up to hundreds of thousands to ~1M msgs/sec |

---

## Scale-trigger cues

Use these to justify architecture evolution:
- Cache: sustained high miss rate, churn, or throughput saturation
- Database: sustained write pressure, rising p99, long backup windows
- App tier: CPU/memory/network near sustained limits
- Queue tier: growing consumer lag and backlog age

---

## "Do not misuse numbers" reminders

- Do not treat ranges as provider guarantees.
- Do not jump to sharding without measured bottlenecks.
- Do not add queues only because write throughput sounds "high" in isolation.
- Always connect numbers to an explicit SLO and traffic pattern.

---

## Rules of thumb

- Optimize for p95/p99, not only average latency.
- Remove network hops before micro-optimizing CPU.
- Batch to reduce round trips.
- Cache hot and repeatable reads, not everything blindly.

---

## Interview usage template

"Given X req/sec, Y latency budget, and Z data size, the current single-node design is/is not sufficient. I will first apply indexing/replicas/caching, and introduce sharding or queue buffering only when measured pressure crosses safe headroom."
