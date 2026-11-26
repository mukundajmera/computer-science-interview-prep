# Time Series Databases - Interview Q&A

## Basic Questions

### 1. Why not just store metrics in a relational DB table?
**A**: At high ingest rates (e.g. 100k points/sec), row/index overhead and B-tree write amplification become extremely expensive. TSDBs optimize for append-only sequential writes, domain-specific compression, and partition pruning.

### 2. What is the core TSDB write pattern?
**A**: Append-only ingestion via a Write-Ahead Log (WAL), buffered in memory (Head block), then flushed as immutable, sorted, and compressed blocks to disk.

### 3. What is downsampling?
**A**: Replacing older fine-grained points (e.g. 1-second resolution) with coarser aggregates (e.g. 1-minute averages or min/max) to reduce storage footprint and speed up historical queries.

### 4. What is a "series" in a TSDB?
**A**: A unique stream of timestamps and values, identified by a metric name and a unique combination of key-value tags (e.g., `cpu_usage{host="A", region="us-east"}`).

### 5. What does "cardinality" mean in TSDBs?
**A**: It is the total number of unique series in the database. High cardinality occurs when you add high-entropy tags (like `user_id`), causing memory and inverted index explosion.

## Intermediate Questions

### 6. How do Bloom filters help TSDB reads?
**A**: They quickly rule out blocks that definitely do not contain a specific series or tag, avoiding unnecessary disk I/O when resolving queries across many time partitions.

### 7. Why partition data by time blocks instead of size?
**A**: Time partitioning localizes recent writes, allows efficient pruning of queries by time range, and makes retention policies trivial (just dropping old directories).

### 8. Explain how Gorilla delta-of-delta compression works for timestamps.
**A**: Instead of storing 64-bit timestamps, it stores the difference between consecutive time deltas. For a steady scrape interval, this difference is 0, which encodes to a single bit, massively reducing storage.

### 9. Explain how Gorilla XOR compression works for values.
**A**: It XORs consecutive floating-point values. If values change slightly, the XOR result has many leading/trailing zeros, allowing the TSDB to only store the few meaningful changed bits.

### 10. How do you design retention tiers?
**A**: Keep raw data on fast SSDs short-term (e.g. 14 days), medium rollups mid-term (90 days), and coarse rollups on object storage (S3) long-term based on query needs and cost.

## Advanced Questions

### 11. How do you handle out-of-order or late-arriving writes?
**A**: Since flushed blocks are immutable, out-of-order points are usually kept in a separate memory buffer in the Head block, or written to overlapping disk blocks that are resolved via merge-sort at query time or during background compaction.

### 12. Compare Push vs Pull ingestion models.
**A**: Push (clients send data) handles ephemeral jobs well but risks thundering herds. Pull (TSDB scrapes clients) provides implicit heartbeats (failure to scrape = down) but requires the TSDB to be able to route to all targets.

### 13. What is the role of the Inverted Index in a TSDB?
**A**: It maps label key-value pairs (e.g. `region="us-east"`) to the internal integer IDs of the series that contain those labels, enabling fast PromQL-style label selectors.

### 14. What are the symptoms of a "compaction spiral"?
**A**: If ingestion outpaces compaction, the disk fills with many small blocks. The inverted index becomes fragmented, CPU spikes, and query latency degrades because queries must merge-sort data from too many files.

### 15. How do you justify a TSDB choice in system design interviews?
**A**: Tie it directly to the ingest scale (points/sec), retention economics (TB/month), and time-range query patterns. Explicitly acknowledge when a simpler relational approach or a generic column store might be sufficient for lower volumes.
