# Strong Answer: Distributed Cloud Storage (S3)

*This is an example of how a candidate might present the design in an interview.*

## 1. Overview and Requirements
**Say:** "To build an S3-like object storage system, we need to support extreme durability (11 nines), high availability, and massive scale—starting at 100 PB. We'll support standard APIs: PUT, GET, DELETE, and Multipart Uploads. Crucially, the system must provide strong read-after-write consistency for new objects and overwrites."

## 2. Decoupled Architecture
**Say:** "The core of the architecture is decoupling metadata from the actual object data. 
- We will have a **Stateless API Gateway** handling auth and routing.
- The **Metadata Service** will store bucket, object, and chunk mappings. I'll use a strongly consistent distributed SQL database like Spanner or CockroachDB for this to guarantee ACID properties and read-after-write consistency.
- The **Blob Storage Nodes** will store the actual bits of data. They are simple servers full of disks (JBOD) running a chunk management daemon."

## 3. The Write Path
**Say:** "When a user PUTs an object, the API gateway breaks the object into fixed-size chunks (e.g., 64MB). It queries the Metadata Service for where to put them, streams the chunks to the Blob Nodes, and waits for successful ACKs. **Only after** the chunks are durably written to the Blob Nodes does the API Gateway commit the final object metadata to the Spanner database. This two-phase approach prevents dangling metadata."

## 4. Durability and Erasure Coding
**Say:** "At 100 PB, standard 3x replication is too expensive—it would require 300 PB of raw storage. Instead, I'll use **Erasure Coding**. If we use an 8+4 scheme, we break a chunk into 8 data pieces and 4 parity pieces, spreading them across 12 different racks. We can lose any 4 of those machines and still reconstruct the data. This gives us higher durability than 3x replication but with only a 1.5x storage overhead (150 PB total)."

## 5. Background Daemons
**Say:** "To maintain the system, we need a few asynchronous daemons. 
- A **Garbage Collector** to delete orphaned chunks when objects are overwritten or multipart uploads are abandoned.
- A **Scrubber Daemon** that continuously reads chunks on disks to verify checksums and fix silent bitrot using the erasure-coded parity shards."
