# Solution: LSM-Tree Key-Value Store

## Overview
This solution implements a Key-Value Store based on the Log-Structured Merge-Tree (LSM-Tree) architecture. It includes a Write-Ahead Log (WAL), a MemTable, immutable SSTables, Tombstones for deletions, and a Compaction process.

## Interview Script
**Say:** "I will design an LSM-Tree Key-Value store to optimize for high write throughput. Every write will be appended to a WAL for durability and then inserted into an in-memory MemTable. When the MemTable is full, it flushes to an immutable SSTable on disk. Deletions will use Tombstones, and background Compaction will merge SSTables to reclaim space and optimize reads."

## Key Implementation Details

1. **Write Path:**
   - Append to `wal.log`.
   - Update `ConcurrentSkipListMap`.
   - If size >= threshold, flush to `.sst` and clear `wal.log`.

2. **Read Path:**
   - Check MemTable. Return if found (handle tombstone).
   - Iterate through SSTables from newest to oldest.

3. **Compaction:**
   - Read all SSTables.
   - Keep the latest value for each key.
   - Drop tombstones (since we merge everything).
   - Write to a new compacted `.sst` and delete the old ones.

## Language Specifics
- **Java:** Uses `ConcurrentSkipListMap` and synchronized blocks for file I/O.
- **Python:** Uses a standard `dict` for the MemTable and `os.path.getmtime` to sort SSTables by creation time.
