# Distributed Object Storage - Comparison

## Raw Storage Durability: Replication vs Erasure Coding

| Concern | 3x Replication | Erasure Coding (8+4 Reed-Solomon) |
|---|---|---|
| **Storage Overhead** | $200\%$ ($100\text{PB}$ data $\rightarrow$ $300\text{PB}$ raw) | $50\%$ ($100\text{PB}$ data $\rightarrow$ $150\text{PB}$ raw) |
| **Durability Level** | Moderate (typically 6-nines) | Extremely High (11-nines) |
| **CPU Overhead** | Low (simple copy) | High (requires matrix math for encoding/decoding) |
| **Rebuild Network Cost** | Low (just copy the missing file from 1 replica) | High (must read 8 chunks over the network to rebuild 1 missing chunk) |
| **Best Use Case** | Small, hot data where latency is critical. | Massive, cold/warm data where cost is the primary driver. |

## Metadata Datastore: RDBMS vs NoSQL (Cassandra)

| Concern | RDBMS (e.g., PostgreSQL) | Wide-Column NoSQL (e.g., Cassandra) |
|---|---|---|
| **Horizontal Scalability** | Difficult (requires manual sharding by bucket_id) | Native (consistent hashing out-of-the-box) |
| **Write Throughput** | Lower (B-tree index updates bottleneck) | Very High (LSM trees handle heavy write loads) |
| **ACID Transactions** | Full support (useful for complex bucket policies) | Limited (eventual consistency, tuned with Quorum) |
| **Versioning Support** | Requires complex joins or triggers | Native via TIMEUUID clustering keys |

## Small Object Storage: Direct Filesystem vs Append-Only Containers

| Concern | Direct OS Filesystem (ext4/XFS) | Append-Only Containers (1GB blobs + SQLite index) |
|---|---|---|
| **Inode Usage** | 1 Inode per object (exhausts OS limits fast) | 1 Inode per 1GB container (virtually no limit) |
| **Disk Fragmentation** | High (1KB files use 4KB blocks) | None (bytes are packed contiguously) |
| **Delete Handling** | Fast (OS unlink) | Requires periodic Garbage Collection / Compaction |
| **Read Latency** | Direct OS lookup (Seek thrashing on HDDs) | Fast index lookup, sequential read capability |

## Cross-links
- [Approach Document](./APPROACH.md)
- [Design Document](./DESIGN.md)
