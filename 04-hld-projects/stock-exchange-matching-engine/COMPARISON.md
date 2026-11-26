# Stock Exchange Matching Engine - Comparison

## Architectural Approaches

| Concern | Database-Backed Matching | In-Memory Sequenced Core (LMAX) |
|---|---|---|
| **Latency** | 10ms - 50ms (Disk/Network I/O) | $< 100\text{ }\mu\text{s}$ (RAM/CPU Cache) |
| **Throughput** | Limited by DB lock contention | $100\text{K}+$ QPS per core (lock-free) |
| **Consistency** | ACID Transactions | Deterministic State Machine |
| **Failover Time** | Seconds (DB promotion) | Sub-millisecond (Hot standby) |
| **Complexity** | Low (Standard CRUD) | High (Custom ring buffers, GC tuning) |

## Data Structure Comparisons for Limit Order Book

| Structure | Insert at Price | Get Best Price | Cancel Order | Notes |
|---|---|---|---|---|
| **Array/List** | $O(N)$ | $O(N)$ | $O(N)$ | Unusable for high frequency. |
| **Max/Min Heap** | $O(\log N)$ | $O(1)$ | $O(N)$ | Fast execution, but cancellation is slow. |
| **TreeMap + HashMap** | $O(\log M)$ | $O(1)$ | $O(1)$ | Optimal. $M$ is number of price levels. HashMap provides instant cancel. |

## Cross-links
- [Design](./DESIGN.md)
- [Approach](./APPROACH.md)
