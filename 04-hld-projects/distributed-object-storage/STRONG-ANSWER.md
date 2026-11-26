# Distributed Object Storage - Strong Answer

## Overview

> Say: "To design a distributed object storage system like S3 handling 100 PB of data, we must fundamentally decouple the architecture into a control plane and a data plane. A massive relational database cannot handle petabytes of binary blobs, and a standard distributed filesystem cannot handle 100,000 QPS of complex metadata lookups. We'll use a scalable NoSQL database for metadata and dedicated, dumb chunk servers for raw bytes."

## Capacity and Trade-offs

> Say: "When storing 100 PB, the two biggest enemies are storage cost and OS inode exhaustion. Standard 3x replication would require 300 PB of raw storage. Instead, I'll use Erasure Coding, specifically Reed-Solomon 8+4. This gives us 11-nines of durability with only a 50% storage overhead. Additionally, to avoid running out of inodes and wasting block space on small 1KB objects, the chunk servers will group objects into 1GB append-only container files, indexed locally via SQLite."

## Read and Write Paths

> Say: "For the Write Path, when a client uploads an object, the API Gateway routes it to a Storage Router. The Router buffers the stream, computes the Erasure Coding chunks, and writes 12 chunks to 12 distinct chunk servers. Once a quorum acknowledges the write, the Router commits the object's `(bucket_name, object_name)` mapping to our Cassandra Metadata DB. The Read Path is the inverse: the Router fetches the logical routing metadata from Cassandra, requests the 8 data chunks from the respective chunk servers, reassembles the payload on the fly, and streams it back to the client."

## Handling Failures

> Say: "To maintain our 11-nines durability guarantee, we cannot wait for users to report missing data. We will deploy background scrubbers on every chunk server to continuously verify checksums. If a disk fails, a dedicated Placement and Repair Service will coordinate reading the surviving chunks from other nodes, recalculating the missing parity or data chunk, and writing it to a healthy node before a subsequent failure can cause permanent data loss."
