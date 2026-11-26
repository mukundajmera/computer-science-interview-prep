# Search Autocomplete - Comparison

## System Storage Strategies

| Concern | Trie Server (In-Memory) | Key-Value Store (Redis) | Relational DB |
|---|---|---|---|
| Latency | Ultra-low (sub-millisecond) | Low (< 5ms) | High (disk I/O) |
| Scalability | Complex sharding | Out-of-the-box cluster | Hard at 48k QPS |
| Complexity | High (Custom build) | Medium | Low |
| Cost | High (RAM is expensive) | High (RAM) | Low (Disk) |

**Key difference:** While an in-memory Trie server is the most optimal for traversal, a distributed Key-Value store (where Key = prefix, Value = Top 5 suggestions JSON) is much easier to scale and maintain operationally. 

## Aggregation Pipelines

| System | Similarity | Key difference |
|---|---|---|
| Real-time Streaming (Flink) | Both aggregate query streams to update search frequencies. | Updates happen in seconds, but complexity is very high. |
| Batch Processing (Hadoop/Spark) | Both aggregate query streams to update search frequencies. | Updates take hours/days, but architecture is robust and simpler. |

## Cross-links
- [Design](DESIGN.md)
- [Approach](APPROACH.md)
