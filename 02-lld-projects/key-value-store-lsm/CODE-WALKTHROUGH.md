# Code Walkthrough

This document traces the evolution of the LSM-Tree Key-Value Store from a basic in-memory map to an optimized, compacted multi-tier storage engine.

## Entry APIs
- `put(key, value)`: Inserts or updates a value.
- `get(key)`: Retrieves a value or returns null/None if absent.
- `delete(key)`: Issues a tombstone marker for deletion.

## Version Delta Table

| Version | Features | Complexity | Correctness Invariants |
|---------|----------|------------|------------------------|
| **v1: Basic** | WAL, MemTable (ConcurrentSkipListMap/dict) | Write: O(log N) (Java) / O(1) amortized (Python). Read: O(log N) / O(1). Space: O(N) memory. | Writes are appended to WAL before MemTable. Restart rebuilds exact MemTable state. Memory unbounded. |
| **v2: Extended** | SSTable flushing, Tombstone deletes | Write: O(log N) + Flush O(M). Read: O(log N) + O(K * M) (K SSTables, M entries). Space: Disk bounded by flush size. | MemTable flushed sequentially when threshold met. WAL deleted only *after* successful flush. Deletions tracked via `<TOMBSTONE>`. |
| **v3: Optimized** | Foreground Compaction | Write: O(log N) + Flush/Compact. Read: O(log N) + O(C * M) (C <= threshold). | Compaction prioritizes newer SSTables over older ones. Tombstones only dropped when merged across all tables. File deletion happens *after* compacted file creation. |

## Path Execution Examples
1. **Write (v1-v3):** `put("k1", "v1")` -> append `k1=v1` to `wal.log` -> insert into `MemTable`.
2. **Read (v3):** `get("k1")` -> check `MemTable` (miss) -> open newest `.sst` (miss) -> open oldest `.sst` (hit).
3. **Delete (v2-v3):** `delete("k2")` -> `put("k2", "<TOMBSTONE>")` -> flush propagates tombstone -> read stops at tombstone returning null.
