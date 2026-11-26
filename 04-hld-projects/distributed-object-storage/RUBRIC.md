# Distributed Object Storage - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
|---|---|---|
| **Requirements Gathering** | 10% | Correctly identifies the scale (petabytes), recognizes the split between metadata and blob payload, and sets strict durability requirements (11-nines). |
| **Data Separation** | 20% | Explicitly decouples the metadata store (e.g., Cassandra) from the blob data store (Chunk Servers), recognizing that no single DB can handle both effectively at $100\text{PB}$ scale. |
| **Storage Efficiency** | 20% | Addresses the "small file problem" by packing small objects into larger append-only containers, eliminating inode exhaustion. |
| **Durability & Resilience** | 25% | Proposes Erasure Coding (e.g., Reed-Solomon) to save storage costs over 3x replication. Discusses background scrubbers and repair services for rebuilding failed chunks. |
| **Component Design** | 15% | Details the read/write paths clearly, including a Storage Router for handling multi-chunk fan-out/fan-in and streaming directly to/from clients. |
| **Trade-offs** | 10% | Effectively compares RDBMS vs. NoSQL for metadata, and Replication vs. Erasure Coding for raw blobs. |

## Performance bands

- **Strong Hire (5/5):** Hits all dimensions flawlessly. Instantly pivots to Erasure Coding and small-file packing (append-only logs) when scale is discussed. Understands network bottlenecks of chunk rebuilds.
- **Hire (4/5):** Separates metadata and blob storage. Mentions Erasure coding but might stumble on exact overheads or rebuild mechanisms. Identifies inode issues but might use generic "batching" rather than strict containerization.
- **Pass (3/5):** Designs a functional system using simple 3x replication and a standard filesystem per chunk node. Needs some hints to realize inode exhaustion or the extreme cost of $200\%$ overhead at $100\text{PB}$.
- **Weak (2/5):** Tries to store large binary blobs directly inside a relational or NoSQL database. Misses the network or storage cost scale completely.
- **Fail (1/5):** Cannot articulate a clear read/write path or handle the basic CRUD operations in a distributed manner.

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design Document](./DESIGN.md)
