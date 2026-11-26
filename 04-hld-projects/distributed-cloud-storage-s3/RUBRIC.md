# Grading Rubric: Distributed Cloud Storage (S3)

## Requirements & Estimation
- **Strong:** Identifies that scale (100 PB) demands decoupling metadata from data. Realizes 99.999999999% durability means multiple AZ redundancy and specific data protection schemes.
- **Okay:** Estimates sizes but doesn't connect it to architectural choices. Misses some core APIs like Multipart Upload.
- **Weak:** Struggles with the API design, or tries to put the object data in a SQL database.

## Architecture & Data Model
- **Strong:** Clearly decouples Metadata DB (strongly consistent) and Blob Nodes. Understands the chunking mechanism and the mapping between logical objects and physical chunks.
- **Okay:** Has separate metadata and blob storage, but doesn't mention chunking. Tries to store whole objects on single nodes.
- **Weak:** Couples metadata and data, or uses a centralized metadata node that would bottleneck.

## Durability & Scalability (Deep Dive)
- **Strong:** Explains the math and mechanism of Erasure Coding vs Replication. Understands the 1.5x vs 3x storage overhead tradeoff. Explains bitrot scrubbing and garbage collection daemons.
- **Okay:** Mentions replication (e.g., 3x) but doesn't mention Erasure Coding. Misses background scrubbing.
- **Weak:** Doesn't explain how durability is achieved at all.

## Consistency & Trade-offs
- **Strong:** Explains how strong read-after-write consistency is achieved by writing to blob nodes first, then committing metadata transactionally to a CP database (CockroachDB/Spanner).
- **Okay:** Mentions consistency but waves hands on how the two-phase write (blob then metadata) actually works.
- **Weak:** Chooses an eventually consistent DB for metadata without understanding the read-after-write implications for PUTs.
