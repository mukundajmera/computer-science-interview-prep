# Database Live Re-sharding & Zero-Downtime Migration

## 📚 Theory
Live re-sharding (or zero-downtime migration) is the process of migrating a database from one cluster topology (e.g., 2 shards) to another (e.g., 4 shards) or to a completely new database engine, without taking down the application or denying write requests. 

This requires a delicate dance of dual-writing, snapshotting, and synchronization to ensure no data is lost or corrupted, while avoiding race conditions between new incoming writes and background backfills.

### The 6-Phase Zero-Downtime Migration Protocol

#### Phase 1: Dual-Write
- **Mechanism:** The application begins writing to both the old (source) database and the new (target) database.
- **Authority:** The old database remains the **authoritative** source of truth for both reads and writes. The new database is treated as a best-effort write.
- **Error Handling:** If writing to the new database fails, the application logs the error but continues; a failure in the new system must not impact availability.

#### Phase 2: Historical Snapshot Backfill
- **Mechanism:** A background process begins copying historical data from the old database to the new one.
- **Chunked Keyspace Paging:** The data is usually copied in chunks (e.g., based on primary key ranges) to avoid overloading the source database.
- **LWW Timestamp Locks:** To prevent the backfill from overwriting newer data that was just written by the dual-write mechanism, a Last-Write-Wins (LWW) resolution is used. Typically, this is achieved by comparing updated_at timestamps. The backfill only inserts or updates a record if the target database doesn't already have a newer version.

#### Phase 3: CDC Catch-up Replication & Reconciliation
- **Mechanism:** Change Data Capture (CDC) systems (e.g., Debezium) stream any missing updates that might have fallen through the cracks (e.g., due to race conditions or failed dual-writes) from the old database's write-ahead log (WAL) to the new database.
- **Merkle Tree Reconciliation:** To verify that the data in the target database perfectly matches the source database, Merkle trees (hash trees) can be used to quickly identify discrepancies in large datasets and trigger targeted repairs.

#### Phase 4: Shadow Reads / Dark Traffic
- **Mechanism:** The application starts sending read requests to *both* the old and the new database.
- **Verification:** The response from the new database is not returned to the user but is compared asynchronously with the response from the old database. Discrepancies are logged and monitored.
- **Goal:** Build confidence that the new database is functionally correct and can handle the read load.

#### Phase 5: Read Cutover & Write Authority Inversion
- **Mechanism:** Once shadow reads prove successful, read traffic is officially routed to the new database.
- **Authority Inversion:** The new database is now designated as the **authoritative** source. The old database becomes the secondary, best-effort target (reverse dual-write).
- **Safety:** This phase allows for a rapid rollback. If issues occur with the new database, the application can immediately fall back to the old one, because the reverse dual-write keeps the old database up-to-date.

#### Phase 6: Decommissioning
- **Mechanism:** After a sufficient observation period (days or weeks) without any issues, the dual-write to the old database is stopped.
- **Cleanup:** The old database is backed up, safely spun down, and destroyed. The migration is complete.

## 🎯 When to Use
- When scaling out a sharded database (e.g., moving from N to 2N shards).
- When migrating to a different database technology (e.g., MySQL to PostgreSQL or NoSQL).
- When altering a very large table schema that cannot be done online.

**Trade-offs:**
- Adds immense complexity to the application code (dual-writing logic).
- Increases latency during the dual-write phases.
- Requires careful handling of race conditions.

## 🏗️ Implementation
Common technologies involved:
- **CDC:** Debezium, AWS DMS (Database Migration Service)
- **Reconciliation tools:** pt-table-checksum, custom Merkle tree implementations
- **Feature Flags:** Used to dynamically toggle phases (e.g., `enable_dual_write`, `enable_shadow_reads`, `enable_read_cutover`).

## 🔗 Cross-References
- [Database Sharding](../database-sharding/)
- [Database Replication](../database-replication/)
- [Data Partitioning](../data-partitioning/)
- [Write Scaling](../write-scaling/)
