# Distributed Cloud Storage (S3) - Common Pitfalls

## 1. Using a centralized metadata node
- **Failure Signal:** Designing the metadata service as a single MySQL instance or an HDFS NameNode.
- **Root Cause:** Failing to appreciate the scale of object storage (billions of small objects), which quickly exhausts the memory or I/O capacity of a single machine.
- **Mitigation:** Distribute the metadata using a horizontally scalable, strongly consistent database like Spanner or CockroachDB.

## 2. Storing entire large files on a single node
- **Failure Signal:** No chunking mechanism; assigning an entire 100GB video file to a single Blob Node.
- **Root Cause:** Missing the need for load balancing and parallel throughput. A single node's network or disk I/O would bottleneck the upload/download, and if the node fails, moving 100GB is slow.
- **Mitigation:** Break files into chunks (e.g., 64MB) and distribute them across the cluster.

## 3. Ignoring cost at Exabyte scale (Overusing Replication)
- **Failure Signal:** Suggesting 3x or 5x replication for everything.
- **Root Cause:** Not calculating the cost of overhead. At 100 PB, a 3x overhead means buying and maintaining 300 PB of drives. 
- **Mitigation:** Use Erasure Coding (e.g., 8+4 or 12+4) for large chunks to achieve higher durability with much lower overhead (e.g., 1.5x).

## 4. Metadata consistency bugs
- **Failure Signal:** Committing metadata before the data chunks are durably written.
- **Root Cause:** Misunderstanding the write path. If metadata is written first and the data upload fails, a GET request will see the metadata but fail to find the data chunks (a dangling pointer).
- **Mitigation:** Write data chunks first, gather their success acks, and *then* commit the metadata to the DB in a single transaction.
