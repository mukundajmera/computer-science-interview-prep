# Approach: Distributed Cloud Storage (S3)

## Goal
To build a highly available, scalable, and extremely durable object storage system suitable for handling unstructured data spanning from small files to multi-terabyte videos.

## High-Level Strategy
1. **Separation of Concerns:** Separate metadata storage from actual object data storage. Metadata operations require ACID properties to prevent concurrency anomalies (e.g., two users creating the same bucket, or overwriting an object concurrently). The actual object storage requires pure scale and high throughput, usually appended continuously without modification to chunks.
2. **Chunking Data:** To achieve high throughput, load-balance storage optimally, and use erasure coding effectively, large files are broken down into fixed-sized chunks (e.g., 64MB).
3. **Optimized Durability (Erasure Coding):** Instead of simple 3x replication which introduces 200% overhead, we will use Erasure Coding for chunks. For instance, 8 data chunks + 4 parity chunks = 12 total chunks spread across 12 different fault domains. This allows the system to lose up to 4 domains simultaneously without data loss, while only having a 50% storage overhead.
4. **Strong Consistency:** When a client successfully PUTs an object and receives an HTTP 200, any immediate GET must read the new version. We guarantee this by committing the chunk metadata into a strongly consistent database (like CockroachDB/Spanner) *after* the blob nodes have safely stored the data chunks.
5. **Background Lifecycle Management:** Garbage collection (cleaning up orphaned chunks), bitrot scrubbing (validating checksums on disks), and multipart upload cleanup are completely decoupled into asynchronous background processes.

## Alternatives Considered
- **All-in-one Storage (e.g., HDFS):** Typically has a single metadata node (NameNode), which becomes a bottleneck at billions of objects. A distributed metadata service is crucial for S3's scale.
- **Cassandra for Metadata:** Cassandra's eventual consistency means read-after-write can fail without quorum, and multi-record transactions (updating object metadata and marking old chunks for deletion) are hard. We chose Spanner/CockroachDB.
