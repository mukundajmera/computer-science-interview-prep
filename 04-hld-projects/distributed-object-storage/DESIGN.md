# Distributed Object Storage - System Design

## 1. 📝 Requirements and Constraints
Refer to [PROBLEM.md](./PROBLEM.md) for the complete problem statement, scope, and capacity requirements.

---

## 2. 📊 Back-of-Envelope Estimation
Refer to [APPROACH.md](./APPROACH.md) for detailed sizing math, including scaling constraints and the choice of Erasure Coding vs Replication.

---

## 3. 🔌 API / System Interface

The system heavily utilizes RESTful principles over HTTP. Due to file size constraints, `PUT` and `GET` are highly prioritized.

### Core Endpoints

**1. Create Bucket**
```http
POST /api/v1/buckets
{
  "bucket_name": "my-app-assets"
}
```

**2. Put Object**
```http
PUT /api/v1/buckets/{bucket_name}/objects/{object_name}
Content-Type: application/octet-stream
[Binary Data]
```

**3. Get Object**
```http
GET /api/v1/buckets/{bucket_name}/objects/{object_name}
```
*Returns binary stream of the object along with ETag and version metadata in headers.*

**4. Delete Object (Versioning)**
```http
DELETE /api/v1/buckets/{bucket_name}/objects/{object_name}
```
*Adds a "Delete Marker" version. Returns 204 No Content.*

**5. Initiate Multipart Upload**
```http
POST /api/v1/buckets/{bucket_name}/objects/{object_name}/uploads
```
*Returns an `upload_id` used for subsequent part uploads.*

---

## 4. 🗄️ Core Entities and Data Model

The data model enforces strict separation between metadata and blob storage. 

### Metadata Database (Cassandra/RDBMS)
Cassandra provides excellent write scalability and multi-region replication. The partition key is often a hash of the `bucket_name` or `bucket_id` to distribute load.

```sql
CREATE TABLE buckets (
    bucket_id UUID PRIMARY KEY,
    bucket_name VARCHAR(63) UNIQUE NOT NULL,
    owner_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE objects (
    bucket_id UUID NOT NULL,
    object_name VARCHAR(1024) NOT NULL,
    version_id TIMEUUID NOT NULL,
    object_id UUID NOT NULL,
    size_bytes BIGINT NOT NULL,
    etag VARCHAR(64) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY ((bucket_id, object_name), version_id)
) WITH CLUSTERING ORDER BY (version_id DESC);
```

### Chunk Server Local Index (SQLite)
Chunk servers store massive 1GB append-only files (containers). An embedded SQLite database on each chunk server translates a global `object_id` into a local physical disk location.

```sql
CREATE TABLE chunk_blocks (
    object_id UUID PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,
    offset_bytes BIGINT NOT NULL,
    length_bytes BIGINT NOT NULL,
    sha256_checksum VARCHAR(64) NOT NULL
);
```

---

## 5. 🏗️ High-Level Architecture

![Architecture Diagram](./diagrams/architecture.mmd)

### Component List
1. **API Gateway:** Handles SSL termination, Authentication, and Rate Limiting.
2. **Metadata Service:** A stateless service handling all interactions with the Metadata Database (Cassandra).
3. **Storage Router (Data Node Manager):** Handles streaming data to/from chunk servers, encoding, and chunk placement.
4. **Chunk Servers (Data Nodes):** Raw storage servers running append-only container managers.
5. **Placement & Repair Service:** Background worker that detects failed disks/nodes and orchestrates Erasure Coding rebuilds.

### Read Path (GET Object)
1. Client calls `GET /bucket/object`.
2. API Gateway routes to the Storage Router.
3. Storage Router calls the Metadata Service to look up `object_name`. It receives the `object_id`, routing locations of chunks, and the `version_id`.
4. Storage Router requests chunks from the respective Chunk Servers.
5. For Erasure Coded files, it fetches 8 data chunks. (If one is missing, it fetches a parity chunk and rebuilds it on the fly).
6. Storage Router streams the reassembled file to the client.

### Write Path (PUT Object)
1. Client calls `PUT /bucket/object` with binary data.
2. Storage Router receives the stream. For large files, it buffers into memory or fast SSD caching tier, applying Erasure Coding (8+4).
3. The Router synchronously writes the 12 chunks to 12 distinct Chunk Servers.
4. Once a quorum (e.g., all 8 data + at least 2 parity) acknowledge the write, the Router commits the object location and metadata to the Metadata Service.
5. Router returns 200 OK to the client.

---

## 6. 🔍 Deep Dives

### Deep Dive A: Storage Efficiency & Append-Only Containers
Writing 680M objects directly to the filesystem would exhaust OS inodes and waste capacity via block fragmentation (a 1KB file uses a 4KB block).
- **Design:** Chunk servers allocate 1GB "Container" files. Incoming chunks are appended to the active container. 
- **Index:** A local SQLite DB maps the chunk ID to `(container_id, offset, length)`.
- **Compaction:** When objects are deleted, their space in the container becomes "dead". A background Garbage Collection job periodically reads fragmented containers, compacts live objects into a new container, and deletes the old one.

### Deep Dive B: Resiliency and Erasure Coding Rebuilds
To guarantee $99.999999999\%$ (11 nines) durability, chunk servers run background scrubbers.
- **Scrubbing:** Processes continually verify the `sha256_checksum` of chunks.
- **Failure:** If a drive dies, the Placement & Repair Service is notified.
- **Rebuild:** It finds the surviving chunks (e.g., 7 data, 4 parity), reads 8 total, reconstructs the missing data, and writes the recovered chunk to a new, healthy chunk server. This must happen fast enough to prevent multi-drive failures from causing permanent data loss.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Redundancy | Erasure Coding (8+4) | 3x Replication | 3x Replication is too expensive ($200\%$ overhead vs $50\%$) for 100PB scale. EC provides 11-nines at lower cost. | If CPU costs for encoding outweigh storage costs for hot data. |
| Metadata DB | Cassandra (NoSQL) | PostgreSQL | Cassandra natively supports high write throughput, seamless horizontal scaling, and TIMEUUID clustering for versioning. | If multi-object transactions become a strict requirement. |
| Small Files | Append-only Containers | Direct Filesystem | Prevents inode exhaustion and disk seek thrashing. | If hardware shifts drastically (e.g., NVMe strictly eliminates seek latency constraints). |

---

## 8. 🔗 Cross-links

- [Problem Statement](./PROBLEM.md)
- [Approach & Sizing](./APPROACH.md)
- [Interview Rubric](./RUBRIC.md)
- [Common Pitfalls](./PITFALLS.md)
- [Follow-up Questions](./FOLLOW-UPS.md)
- [Comparisons](./COMPARISON.md)
- [Strong Answer Example](./STRONG-ANSWER.md)

---
**Real-world reference**: See how Amazon solved this in the [Amazon case study](../../case-studies/amazon-orders/)
