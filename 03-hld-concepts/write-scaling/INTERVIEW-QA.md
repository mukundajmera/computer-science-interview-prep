# Write Scaling Interview Q&A

1. **What is your shard-key fallback if skew appears?**
   If a chosen shard key exhibits skew (a hot partition), a fallback is to use compound keys (e.g., `user_id` + `hash(timestamp)`), or to apply "salting" to distribute the hot key's traffic artificially across multiple shards, handling the re-aggregation logic on the read side.

2. **How do you handle Black Friday-style write bursts?**
   By decoupling ingestion from processing using message queues (e.g., Kafka). The burst is rapidly appended to the queue, and consumers process it at the database's maximum sustainable rate, buffering the spike.

3. **When is load shedding acceptable?**
   When the queue is full, back-pressure has failed to slow producers, and system failure (OOM, DB crash) is imminent. It is better to reject a percentage of requests (returning 429 or 503) and keep the system alive than to crash completely and serve zero requests.

4. **How do you recover from queue backlog growth?**
   First, identify the bottleneck (usually the database or the consumer compute). Scale out consumers if compute is the issue. If the DB is the issue, optimize queries, increase batch sizes, or temporarily pause non-critical workloads to let the backlog drain.

5. **How do you migrate from 8 to 16 shards online?**
   Using a dual-write approach: 1. Deploy code that writes to both old and new shard topologies. 2. Run a background script to backfill historical data from old to new shards. 3. Validate data integrity between both. 4. Switch reads to the new topology. 5. Stop dual-writes and decommission the old shards.

6. **What is group commit and how does it improve throughput?**
   It is a database optimization where multiple concurrent transactions are delayed slightly to be written to the Write-Ahead Log (WAL) in a single disk fsync. This amortizes the cost of the fsync across many transactions, drastically increasing IOPS efficiency.

7. **Explain the difference between write-through and write-behind caching.**
   Write-through synchronously writes data to both the cache and the database before returning success, ensuring consistency at the cost of latency. Write-behind writes only to the cache and asynchronously flushes to the DB later, maximizing speed but risking data loss if the cache fails.

8. **Why are LSM trees better for write-heavy workloads than B-Trees?**
   LSM trees transform random writes into sequential writes by appending to an in-memory structure and an on-disk log, which is much faster for disk IO. B-Trees require traversing and updating disk blocks in place, leading to write amplification and random IO overhead.

9. **What is back-pressure in a streaming architecture?**
   It is a mechanism where a downstream component (e.g., a slow database consumer) signals to an upstream component (e.g., an API gateway) to slow down the rate of data generation because it cannot keep up, preventing buffer overflows.

10. **How does batching help with network overhead?**
    Sending 100 individual HTTP requests or DB queries incurs network latency and protocol overhead 100 times. Batching them into a single payload incurs the overhead only once, vastly improving the ratio of useful data to overhead.

11. **Describe a scenario where strong consistency is required for writes.**
    Financial transactions, such as transferring money between bank accounts, require strong consistency (ACID guarantees). The write must be durably committed and instantly visible to prevent double-spending or data anomalies.

12. **How do you ensure idempotency in a distributed write system?**
    By having clients generate unique idempotency keys (e.g., UUIDs) for each operation. The server checks these keys against a fast store (like Redis) or database constraints before executing the write to ensure it hasn't already been processed.

13. **What is write amplification?**
    It occurs when a small logical write request by an application results in a much larger amount of physical data being written to the underlying storage media, often due to page fragmentation or B-tree rebalancing.

14. **How do you mitigate deadlocks in a high-concurrency write environment?**
    Ensure all transactions acquire locks in the exact same predefined order (e.g., sorting keys lexicographically before updating). Alternatively, use optimistic concurrency control where transactions proceed without locks and abort/retry if a conflict is detected upon commit.

15. **What are the trade-offs of using an append-only architecture?**
    It provides extremely fast writes and inherent versioning (event sourcing). The trade-offs include higher storage consumption (until compacted), slower reads (requiring sequential scans or separate indexing), and the complexity of eventual compaction and snapshotting.
