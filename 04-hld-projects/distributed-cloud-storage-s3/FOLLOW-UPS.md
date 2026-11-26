# Follow-Up Questions: Distributed Cloud Storage (S3)

## 1. Hot Partitions in Metadata DB
**Q:** What happens if a user uploads millions of objects sequentially with keys like `logs/2023-10-24/0001`, `logs/2023-10-24/0002`?
**A:** In a distributed database like Spanner, sequential keys often land on the same partition (tablet), creating a hot spot and throttling write QPS. To mitigate this, we can suggest users prepend a random hash to the key (e.g., `a7c-logs/...`, `b29-logs/...`) to distribute the writes across multiple partitions, or the metadata service can automatically hash the keys internally before storing them in the DB.

## 2. Multipart Upload State
**Q:** If a user initiates a multipart upload, uploads 5 out of 10 parts, and then abandons it, what happens to the stored data?
**A:** It wastes space. We need a background Garbage Collection (GC) daemon or Lifecycle Manager that sweeps the `MultipartUpload` metadata tables. If an upload is older than a configured threshold (e.g., 7 days) and hasn't been completed, the GC daemon marks the associated data chunks for deletion and cleans up the upload metadata.

## 3. Bitrot and Silent Data Corruption
**Q:** How do you ensure the 11 9s of durability when hard drives silently flip bits (bitrot)?
**A:** A background Scrubber daemon continuously reads chunks from disk during idle periods, calculates their checksum, and compares it against the expected checksum. If there's a mismatch (bitrot), it fetches the parity chunks from other nodes, reconstructs the original chunk, and writes it to a healthy disk.

## 4. Cross-Region Replication (CRR)
**Q:** How would you support asynchronously replicating a bucket to another geographical region?
**A:** The API Gateway or Metadata Service can emit an event to a message queue (e.g., Kafka) when an object is successfully written. A cross-region replication worker consumes this event, reads the object from the source region, and PUTs it to the destination region asynchronously.
