# Approach: LSM-Tree Key-Value Store

## 1. Write Path
- **WAL Append:** Every `put` or `delete` is first written to an append-only Write-Ahead Log to guarantee durability.
- **MemTable Insertion:** The entry is then added to the in-memory MemTable (a ConcurrentSkipListMap in Java, or a dict in Python).
- **Flushing:** Once the MemTable size hits a predefined threshold, its contents are written to a new SSTable file on disk. The MemTable is then cleared, and the WAL is truncated or deleted.

## 2. Read Path
- **MemTable Lookup:** The query first checks the MemTable, as it contains the most recent updates.
- **SSTable Lookup:** If the key is not found, the system searches the SSTables starting from the most recently created one to the oldest.
- **Tombstone Handling:** If a tombstone marker is found during either lookup, the system returns `null`/`None`, indicating the key was deleted.

## 3. Deletion
- Deletions are implemented as a special `put` operation where the value is set to a unique `<TOMBSTONE>` marker. This ensures that deletes are durable and correctly hide older values in SSTables.

## 4. Compaction
- Over time, SSTables accumulate. Compaction reads multiple SSTables, merges them, resolves conflicts (keeping the newest value), drops tombstones if appropriate, and writes the result to a new, larger SSTable. It then deletes the old SSTables.

## 5. Durability and Crash Recovery
- **Crash Points:** The implementation supports injected crash points during WAL append/flush and memtable/SST publication.
- **Recovery:** Acknowledged operations are recovered under the stated simulated durability contract. Corrupt or truncated records in the WAL are safely ignored/discarded during recovery, and idempotent duplicate replays are supported.

## 6. Advanced Lookups and Compaction Guarantees
- **Bloom Filters:** To reduce disk I/O, SSTables utilize Bloom filters. Since Bloom filters may yield false positives, any positive match strictly triggers an exact lookup fallback in the underlying SSTable data.
- **Tombstone Survival & Range Boundaries:** Latest-write/delete tombstones explicitly survive compaction merges and store reopens. Range boundary edge cases are explicitly handled and tested during both query and compaction phases.
