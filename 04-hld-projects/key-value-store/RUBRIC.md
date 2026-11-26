# Interview Rubric: Key-Value Store

| Signal | Criteria |
|---|---|
| **Data Partitioning** | Identifies consistent hashing; uses virtual nodes for load balancing. |
| **Replication** | Explains N/R/W quorum arithmetic; understands consistency vs availability tradeoffs. |
| **Conflict Resolution** | Details vector clocks; distinguishes causality from physical time (LWW). |
| **Failure Handling** | Explains hinted handoff for transient failures; anti-entropy (Merkle trees) for permanent failures. |
| **Local Storage** | Describes LSM-tree architecture, MemTable, SSTables, and WAL. |
