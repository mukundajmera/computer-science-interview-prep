# Distributed Object Storage - Common Pitfalls

## 1. Storing Blobs in the Database
- **Signal:** Candidate designs a single massive Cassandra or PostgreSQL cluster and proposes storing the `byte[]` payload directly in a column.
- **Root Cause:** Treating an object storage system like a standard CRUD application, ignoring the fundamental difference between metadata (kilobytes, structured) and blobs (megabytes to gigabytes, unstructured).
- **Mitigation:** Explicitly separate the control plane (Metadata DB) from the data plane (Chunk Servers).
- **Validation:** Ensure the data model only stores `object_id` references, while the physical bytes are routed to dedicated storage nodes.

## 2. Ignoring the "Small File Problem"
- **Signal:** Candidate assumes files are just written directly to standard Linux file systems (like ext4) as `/data/bucket/object.jpg`.
- **Root Cause:** Lack of awareness regarding OS inode limits and block fragmentation. At 680 million objects, a standard filesystem will exhaust inodes long before disk space, and 1KB files will waste 4KB blocks.
- **Mitigation:** Propose an append-only WAL or containerization strategy. Pack hundreds of small files into a single 1GB container file, indexing offsets internally via SQLite.
- **Validation:** Ask the candidate how many files an ext4 filesystem can hold, and how they would store 1 billion 500-byte images.

## 3. Relying Solely on 3x Replication for $100\text{PB}$ Scale
- **Signal:** Candidate mandates standard 3x replication for all data without acknowledging the massive cost implication.
- **Root Cause:** Reusing standard distributed DB patterns without doing the storage cost math. $100\text{PB}$ of data with 3x replication requires $300\text{PB}$ of raw disks.
- **Mitigation:** Introduce Erasure Coding (e.g., Reed-Solomon 8+4) to provide higher durability (11-nines) with only $50\%$ storage overhead ($150\text{PB}$ raw).
- **Validation:** Force the candidate to calculate the raw storage overhead and cost difference between replication and Erasure Coding.

## 4. Inefficient Multipart Upload Assembly
- **Signal:** Candidate designs multipart upload such that a single coordinator node must download all parts locally to stitch them together before saving.
- **Root Cause:** Creating a massive network and disk I/O bottleneck on the coordinator.
- **Mitigation:** Parts should be uploaded directly to chunk servers. The metadata DB simply tracks the list of chunks forming the object. Reassembly only happens virtually at read time (streaming parts sequentially).
- **Validation:** Ask how a 5TB object is handled during a multipart upload.
