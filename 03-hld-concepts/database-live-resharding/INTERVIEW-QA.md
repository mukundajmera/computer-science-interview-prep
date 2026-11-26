# Database Live Re-sharding - Interview Q&A

1. **How do you handle race conditions during the backfill phase if a record is updated via dual-write at the exact same time the backfill is trying to copy the old version?**
   > Say: "We use Last-Write-Wins (LWW) conflict resolution during the backfill. Every row must have an `updated_at` timestamp. Before the backfill process inserts or updates a row in the target database, it compares the timestamp. If the target database already has a newer timestamp (from the dual-write mechanism), the backfill skips that row, preventing older snapshot data from overwriting newer dual-written data."

2. **What happens if a write to the new (target) database fails during Phase 1 (Dual-Write)?**
   > Say: "During Phase 1, the old database is authoritative and the new database is a best-effort write. If a write to the new database fails, we catch the exception, log the error, and emit a metric, but we return a success response to the client. This ensures the migration does not degrade the availability of the primary system."

3. **How do you ensure no data is lost if the dual-write mechanism experiences a prolonged outage or network partition to the target cluster?**
   > Say: "We rely on Change Data Capture (CDC) streaming the write-ahead log (WAL) as a safety net (Phase 3). Even if the dual-write fails in the application layer, the CDC pipeline will eventually catch up and asynchronously replicate those missed writes to the target database, maintaining eventual consistency."

4. **Why is the Shadow Read (Dark Traffic) phase necessary? Can't we just trust that the data was copied correctly?**
   > Say: "Shadow reads are essential for two reasons. First, they verify data integrity under real production workloads, surfacing subtle edge cases or data corruption that static backfills might miss. Second, they act as a capacity test to ensure the new cluster can handle the read volume before we officially cut over, preventing a sudden overload."

5. **How do you rollback if the new database starts corrupting data immediately after the Read Cutover (Phase 5)?**
   > Say: "Because Phase 5 includes a 'reverse dual-write' (writing authoritatively to the new DB and best-effort to the old DB), the old database remains up-to-date. If corruption is detected, we simply toggle the feature flags back to Phase 4 or Phase 1, reverting the read and write authority back to the old database immediately, with no data loss."

6. **What is a Merkle tree and how is it used during continuous data reconciliation?**
   > Say: "A Merkle tree is a hash tree where leaves are hashes of individual rows and parent nodes are hashes of their children. During the migration, we can compute Merkle trees for data ranges on both the source and target databases. By comparing the root hashes, and then walking down the tree where hashes differ, we can quickly isolate exactly which rows are out of sync without transferring all the data across the network."

7. **How do you manage the extra latency introduced by dual-writing?**
   > Say: "We can perform the dual-write asynchronously. The application writes synchronously to the authoritative database, and then fires off an asynchronous task (e.g., via an in-memory queue or background thread) to write to the secondary database. This keeps the client-facing latency unchanged, at the cost of slight eventual consistency in the target."

8. **If the schema is changing during this migration, where does the translation happen?**
   > Say: "The translation logic is typically housed in a dedicated Data Access Object (DAO) or a specific migration layer within the application code. This layer reads the old format, transforms it into the new format, and then performs the dual-write. Similarly, the backfill and CDC pipelines must include this transformation logic."

9. **How do you page through a massive keyspace during the historical backfill without locking the source database or causing performance degradation?**
   > Say: "We avoid `OFFSET/LIMIT` pagination, which gets progressively slower. Instead, we use keyset pagination (chunking by primary key ranges). We query for a batch of records where `id > last_seen_id LIMIT 1000`. We also throttle the backfill worker to a specific QPS to ensure it doesn't impact the production read/write workloads on the source database."

10. **How do you know when the CDC catch-up phase (Phase 3) is finished and it is safe to move to shadow reads?**
    > Say: "We monitor the CDC replication lag. When the lag drops consistently to near zero (e.g., milliseconds), and our continuous data reconciliation jobs (using Merkle trees or full table checksums) report a 100% match or an acceptable threshold of discrepancies that are actively resolving, we can safely proceed to the shadow read phase."
