# Grading Rubric

| Level | Goal | Acceptance Criteria |
|---|---|---|
| **L4 (Beginner)** | Intuitive Minimum Example | Successfully implements `v1-basic`. MemTable holds data, WAL ensures durability. Crash recovery reconstructs state accurately. Code is thread-safe (Java) or functionally correct (Python). |
| **L5 (Senior)** | Trade-offs & Multi-tier | Implements `v2-extended` or `v3-optimized` functionality. Clearly explains threshold-based flushing vs. memory pressure. Understands the cost of synchronous compaction and linear SSTable scanning. Successfully implements Tombstone mechanics. |
| **L6/L7 (Staff)** | Failure Trace & Assumptions | Identifies concrete edge cases: data loss on early WAL deletion, tombstone resurrection, concurrency race conditions during flush/compact. Defends architectural choices based on explicit I/O capacity, memory limits, and target workload profiles (read-heavy vs. write-heavy) without assuming deployed scale. |

## Core Evaluation Focus
- **Correctness over Buzzwords:** Evaluate the actual logic for WAL synchronization, SSTable merge ordering, and Tombstone application, rather than just the mention of "LSM Tree."
- **Defensible Trade-offs:** Can the candidate explain *why* they chose a ConcurrentSkipListMap over a standard HashMap for the MemTable in this specific use case?
