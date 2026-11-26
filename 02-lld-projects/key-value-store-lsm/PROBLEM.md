# Problem: LSM-Tree Key-Value Store

Design and implement a Key-Value Store based on the Log-Structured Merge-Tree (LSM-Tree) architecture. The store should support fast writes and efficient reads, handling crash recovery and eventual garbage collection.

## Requirements

1. **Basic Operations:**
   - `put(key, value)`: Insert or update a key-value pair.
   - `get(key)`: Retrieve the value for a given key.
   - `delete(key)`: Remove a key-value pair.

2. **Components to Implement:**
   - **MemTable:** An in-memory sorted structure (e.g., SkipList) to hold the most recent writes.
   - **Write-Ahead Log (WAL):** An append-only log file to ensure durability and crash recovery.
   - **SSTables (Sorted String Tables):** Immutable files on disk containing flushed MemTable data.
   - **Tombstones:** A mechanism to mark keys as deleted.
   - **Compaction:** A background process (or threshold-triggered process) to merge SSTables, remove deleted/stale keys, and reclaim disk space.

3. **Behavior:**
   - Writes are appended to the WAL and then added to the MemTable.
   - When the MemTable reaches a certain threshold, it is flushed to an SSTable on disk, and a new MemTable/WAL is created.
   - Reads check the MemTable first, then scan SSTables from newest to oldest.

## Scope and Versions

No production/security promise is inferred.
The project is divided into three versions:
*   **v1-basic:** Core LSM structure (MemTable, WAL, SSTable flushing). Deterministic fixture inputs and expected outputs must be explicitly fixed.
*   **v2-extended:** Added support for deletes (tombstones) and basic compaction. Latest-write/delete tombstones must survive compaction and reopen.
*   **v3-optimized:** Advanced features including Bloom filters (Bloom positives must use exact lookup).

## Acceptance Criteria
*   Injected crash points around WAL append/flush and memtable/SST publication recover acknowledged operations under a simulated durability contract.
*   Latest-write/delete tombstones survive compaction and reopen; corrupt/truncated records, duplicate replay and range boundaries are tested.
*   Bloom positives use exact lookup.
