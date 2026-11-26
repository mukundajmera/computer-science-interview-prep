# Distributed Cloud Storage (S3) - Comparison

## Metadata Databases

| DB Type | Similarity | Key Difference |
|---|---|---|
| **CockroachDB / Spanner** | Both provide horizontal scalability and SQL-like interfaces. | Both provide strong consistency and distributed transactions, which is crucial for read-after-write consistency in object storage. |
| **Cassandra** | Highly scalable and distributed. | Eventually consistent by default. Multi-record ACID transactions are limited, making it difficult to guarantee atomicity when updating object pointers and deleting old chunks. |
| **HDFS NameNode (Classic)** | Manages metadata for distributed files. | Classic HDFS uses a single Active NameNode (kept in memory), which becomes a hard bottleneck for billions of small files. Modern object stores distribute the metadata. |

## Durability Mechanisms

| Mechanism | Storage Overhead | Compute Overhead | Fault Tolerance (Nodes lost) | Best For |
|---|---|---|---|---|
| **3x Replication** | 3.0x (200% extra) | Low | 2 | Small objects, high-performance local reads. |
| **Erasure Coding (8+4)** | 1.5x (50% extra) | High (Encoding/Decoding CPU) | 4 | Large objects, cold storage, massive scale cost savings. |
