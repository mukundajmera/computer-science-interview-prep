# Strong Answer: LSM-Tree Architecture

This guide outlines a coherent progression from a basic concept to a Staff-level defense, designed for a 45-minute technical interview. It links the concepts demonstrated in `v1-basic`, `v2-extended`, and `v3-optimized`.

## Target Pacing (45 mins)
- **0-10 min:** Requirements & Architecture Discussion. Define the WAL, MemTable, and SSTables as a simulated proof-of-concept. Avoid claiming production deployment readiness without caveats.
- **10-25 min:** Core Implementation (`v1-basic`). Write path (WAL append + MemTable put) and Read path (MemTable lookup).
- **25-35 min:** Flushing & Deletions (`v2-extended`). Transitioning from memory to disk. Implementing Tombstone markers to hide older data.
- **35-45 min:** Compaction & Failure Defense (`v3-optimized` and `PITFALLS.md`). Discussing merge logic, lost updates, and concurrency boundaries.

## Interview Dialogue Path

### 1. The Foundation (Beginner)
**Say:** "To guarantee durability while maintaining fast writes, I will implement a Log-Structured Merge-Tree (LSM-Tree) architecture. Writes will be appended to a Write-Ahead Log (WAL) and then inserted into an in-memory MemTable. This provides O(1) amortized or O(log N) writes without immediate disk seek penalties."

### 2. Transition to Disk (Senior)
**Say:** "Memory is bounded. Once the MemTable reaches a specific threshold, it must be flushed to an immutable SSTable on disk. For thread safety during this process, I use a `ConcurrentSkipListMap` (or appropriately locked dictionary), which maintains keys in sorted order—critical for sequential flushing."

### 3. Deletions and Compaction (Senior/Staff)
**Say:** "Deletions are handled by writing a unique `<TOMBSTONE>` marker. This ensures the delete is durable and overrides older values during read scans. To prevent infinite file growth, a compaction routine periodically merges SSTables, prioritizing newer tables over older ones, and strictly preserving tombstones unless we can guarantee no older data exists."

### 4. Failure Handling & Trade-offs (Staff)
**Say:** "System crashes are handled by replaying the append-only WAL. Crucially, the WAL is only deleted *after* an SSTable is successfully `fsync`'d to disk. In a simulated environment, synchronous flushes work, but in a production system subject to explicit I/O capacity limits, I would shift compaction to a background thread and introduce Bloom Filters to optimize the read path (see `FOLLOW-UPS.md`)."
