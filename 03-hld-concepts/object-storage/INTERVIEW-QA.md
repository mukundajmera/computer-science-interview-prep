# Object Storage - Interview Q&A

**Q: What is the difference between Object Storage and Block Storage?**
**A:** Block storage provides raw storage volumes over a network (like a virtual hard drive) that requires an OS filesystem to manage it. It offers low latency and allows partial in-place updates. Object storage manages data as objects in a flat bucket structure with robust metadata over HTTP/REST APIs. It scales infinitely and is cheaper, but has higher latency and requires full-object replacement for updates.

**Q: Why does Object Storage use a flat namespace instead of a hierarchy?**
**A:** Hierarchical file systems require managing complex directory trees, tracking locks, and validating permissions down the tree for every operation. At massive scale (billions of files), directory traversal becomes a severe bottleneck. A flat namespace (Key-Value) allows O(1) metadata lookups and seamless horizontal partitioning across millions of servers.

**Q: How does Erasure Coding differ from Replication?**
**A:** Replication keeps $N$ full copies of the data (e.g., 3x). It provides fast reads but high storage overhead (300%). Erasure Coding uses mathematics (like Reed-Solomon) to split data into $K$ chunks and calculate $M$ parity chunks. It can survive $M$ failures with much lower overhead (e.g., 33% overhead for $12+4$), saving massive amounts of raw disk space, but requires CPU cycles to calculate and incurs a network penalty during rebuilds.

**Q: Explain how strong read-after-write consistency works in modern S3.**
**A:** When a client issues a PUT request, the data chunks are persisted to the storage nodes. Crucially, the metadata index is then updated using a distributed consensus protocol (like Raft or Paxos). The PUT request only returns 200 OK after this metadata quorum is achieved. Any subsequent GET request will hit the updated, strongly-consistent metadata index, ensuring it reads the new data, completely eliminating the eventual consistency window for overwrites.

**Q: What happens if a disk silently corrupts data (bit rot) in an object store?**
**A:** Object storage systems calculate and store a cryptographic checksum (e.g., CRC32C, MD5) alongside the data. During a read operation, the checksum is verified. If there's a mismatch, the read path pulls parity chunks (if Erasure Coded) or replica chunks from other nodes to reconstruct the correct data dynamically. Concurrently, a background scrubbing process constantly reads resting data, verifying checksums and initiating asynchronous repairs.

**Q: Why is Multipart Upload necessary, and how does it work?**
**A:** Uploading a 50GB file over a single TCP stream is risky; if it drops at 49GB, the entire upload is lost. Multipart Upload breaks the file into smaller chunks (e.g., 50MB). The client requests an Upload ID, uploads the parts concurrently in separate HTTP requests, and finally calls Complete with a list of part checksums (ETags). The storage system logically stitches them together, offering better resilience and speed.

**Q: If you have millions of small 10KB files, why is object storage inefficient, and how do systems fix this?**
**A:** Each object requires a metadata entry. For a 10KB file, the metadata overhead and minimum Erasure Coding block sizes waste space and create heavy IOPS load on the metadata DB and physical HDDs. Systems fix this by "packing" (like Haystack). Small files are buffered and appended into a large 64MB container file. The metadata index tracks the container ID, offset, and length for each small object.

**Q: How do you prevent hotspots when writing millions of logs to a specific prefix like `bucket/logs/2023/10/`?**
**A:** Object storage metadata is lexicographically sorted. Sequential keys hit the same metadata partition, causing a write bottleneck. You should introduce entropy (randomness) at the start of the key, for example: `bucket/logs/3f2a/2023/10/`. (Note: Modern S3 auto-scales partitions dynamically, but heavy, sudden spikes still benefit from key hashing).

**Q: How does Versioning prevent data loss from accidental overwrites?**
**A:** When Versioning is enabled, a PUT operation to an existing key does not overwrite the physical bytes. Instead, it creates a new physical object and assigns it a unique Version ID. The metadata index links the key to the new version as the 'current' one. A DELETE operation simply writes a 'Delete Marker' as the latest version, leaving the original data intact for recovery.

**Q: What is the purpose of Storage Classes or Tiering?**
**A:** Not all data is accessed equally. Storage classes allow trading latency and retrieval cost for storage cost. Hot/Standard tiers use faster disks and keep data readily available. Archive tiers (like Glacier) move data to spun-down HDDs or tape libraries, dropping the storage cost significantly but requiring minutes or hours to retrieve data.

**Q: How do you secure data in an Object Storage bucket?**
**A:** At the network level: TLS/SSL for in-transit encryption. At the bucket level: Bucket Policies and IAM Roles control access. For data at rest: Server-Side Encryption (SSE) where the provider manages keys, SSE-KMS for auditability, or Client-Side Encryption where data is encrypted before upload.

**Q: What is a Pre-signed URL, and what architectural problem does it solve?**
**A:** A pre-signed URL is a temporary URL generated by a backend server using its secret keys, granting limited time/action access to an object. It solves the bandwidth bottleneck problem: instead of a client uploading a 1GB video to your web server, and the web server uploading to S3, the client uploads *directly* to S3 using the pre-signed URL, offloading the heavy network traffic.

**Q: How does a background scrubber work?**
**A:** A scrubber is a low-priority daemon process running on storage nodes. It sequentially reads data from the physical disks and calculates the checksum. It compares this against the expected checksum stored in the metadata. If it finds corruption (bit rot), it notifies a repair service to reconstruct the chunk from replicas or parity and overwrite the bad block.

**Q: In an erasure-coded system ($12+4$), what happens during a degraded read?**
**A:** A degraded read occurs when the specific node holding a data chunk is offline. The system cannot just read the chunk. Instead, it must read $K$ (12) *other* chunks (data or parity) from the network, perform Reed-Solomon polynomial decoding on the CPU to reconstruct the missing chunk, and then serve it to the client. This introduces a significant latency and network penalty.

**Q: Why would you use Object Lock / WORM?**
**A:** Write Once, Read Many (WORM) is used for strict compliance and legal holds (e.g., financial records, medical data). It ensures that even the root administrator or a compromised application cannot delete or overwrite the object until the retention period strictly expires. It protects against ransomware and rogue actors.
