# File Storage — Model Answer (Time-Boxed)

Say: "I will split metadata from blob storage, make uploads resumable and verifiable, and treat sharing permissions as part of the read path rather than a UI-only feature."

A strong-answer outline for a 40-minute File Storage system design interview. Each section includes target timing and the key points an interviewer expects to hear.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## ⏱️ Time Allocation

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Requirements & Clarification | 5 min | Scope the problem |
| 2. Estimation | 5 min | Quantify scale |
| 3. API + Data Model + High-Level Design | 10 min | Core architecture |
| 4. Deep Dives | 15 min | Chunking, dedup, sync, metadata |
| 5. Trade-offs & Wrap-up | 5 min | Justify decisions, summarize |

---

## Phase 1 — Requirements & Clarification (5 min)

### Clarifying Questions to Ask

1. "What's the expected scale — registered users, DAU, daily uploads?"
2. "What's the average and maximum file size?"
3. "Do we need real-time sync across devices, or is periodic sync acceptable?"
4. "What level of file sharing is required — link-based, permission-based, or both?"
5. "How many versions should we retain per file?"
6. "Should we support selective sync (different folders on different devices)?"

### Functional Requirements (confirm with interviewer)

- **Core:** Upload, download, and delete files and folders; sync across devices; share files/folders with permissions.
- **Important:** File versioning, chunked and resumable uploads for large files.
- **Optional:** Full-text search across file contents, real-time collaborative editing.

### Non-Functional Requirements (state explicitly)

- **Availability:** 99.9% — downtime means users can't access their files across any device.
- **Durability:** 99.999999999% (11 nines) — losing a user's file is unacceptable.
- **Latency:** < 500 ms for metadata operations; upload/download speed bound by bandwidth.
- **Consistency:** Strong consistency for metadata (user sees file immediately after upload); eventual consistency for cross-device sync (seconds-level propagation).
- **Storage:** Petabyte-scale content storage, terabyte-scale metadata.

### Scope Boundaries

- **In scope:** Upload/download, sync, sharing, versioning, chunking, deduplication.
- **Out of scope:** Real-time collaborative editing (Google Docs), media transcoding, full-text search (mention as extension).

---

## Phase 2 — Estimation (5 min)

### Traffic

```
Users:         500M registered, 100M DAU
Daily uploads: 1 billion files/day
Upload rate:   1B / 86,400 ≈ 11,500 files/sec (peak ~35,000/sec)
```

### Storage

```
Total files:     500M users × 1,000 files = 500 billion files
Average size:    1 MB per file
Raw storage:     500B × 1 MB = 500 PB
With dedup (~40%): ~300 PB effective storage
Metadata:        500B files × 1 KB = 500 TB
```

### Bandwidth

```
Upload ingress:  11,500 files/sec × 1 MB = 11.5 GB/s
With dedup:      ~7 GB/s (40% of chunks already exist)
Download egress: Assume 2× upload ≈ 23 GB/s
```

### Chunks

```
Chunk size:      4 MB
Avg file:        1 MB → 1 chunk (most files fit in a single chunk)
Max file (10 GB): 10 GB / 4 MB = 2,500 chunks
Total blocks:    ~500B (with dedup, far fewer unique blocks)
```

### Cache

```
Active users' hot metadata: 100M users × 50 hot files × 200 B ≈ 1 TB
Redis cluster: 10–20 nodes at ~64 GB each
```

---

## Phase 3 — API + Data Model + High-Level Design (10 min)

### API Endpoints

| Method | Endpoint | Purpose | Key Response |
|--------|----------|---------|--------------|
| `POST` | `/api/v1/files/upload-session` | Initiate chunked upload | `201` with `sessionId`, `missingChunks[]`, `presignedUrls[]` |
| `PUT` | Pre-signed S3 URL | Upload a single chunk | `200` OK |
| `POST` | `/api/v1/upload-session/{id}/complete` | Finalize upload | `200` with `fileId`, `version` |
| `GET` | `/api/v1/files/{fileId}/download` | Get download URL | `200` with signed URL or CDN redirect |
| `GET` | `/api/v1/sync/delta?cursor={seq}` | Get sync events since cursor | `200` with events list, new cursor |
| `POST` | `/api/v1/shares` | Share a file/folder | `201` with share link |
| `DELETE` | `/api/v1/files/{fileId}` | Soft-delete a file | `204` No Content |

**Error codes to mention:** `400` (invalid request), `404` (not found), `409` (sync conflict), `413` (file too large), `429` (rate limited).

### Data Model

```
Table: files                            Table: blocks
───────────────────────────────         ─────────────────────────────
file_id       UUID (PK)                 block_id      UUID (PK)
user_id       UUID (FK, partition key)  content_hash  STRING (UK, SHA-256)
folder_id     UUID (FK)                 storage_path  STRING (S3 key)
name          STRING                    size_bytes    BIGINT
size_bytes    BIGINT                    ref_count     INT
content_hash  STRING (SHA-256)          created_at    TIMESTAMP
current_ver   INT
is_deleted    BOOLEAN                   Table: file_blocks (junction)
created_at    TIMESTAMP                 ─────────────────────────────
updated_at    TIMESTAMP                 file_id       UUID (FK)
                                        version_num   INT
Table: file_versions                    block_index   INT
───────────────────────────────         block_id      UUID (FK)
version_id    UUID (PK)
file_id       UUID (FK)
version_num   INT
size_bytes    BIGINT
content_hash  STRING
modified_by   UUID (FK)
created_at    TIMESTAMP
```

- **Database choice:** PostgreSQL for metadata (strong consistency, transactional version updates, complex folder queries). S3 for block content (11 nines durability, infinite scale).
- **Indexes:** `files(user_id, folder_id, name)` for folder listing; `blocks(content_hash)` for dedup; `file_versions(file_id, version_num)` for version history.
- **Cache:** Redis cluster — metadata cache, upload session state, folder tree cache.

### High-Level Architecture

```
Clients (Desktop / Mobile / Web)
    │
    ├─ Upload: chunks via pre-signed URLs ─────────────────→ S3 Block Store
    │                                                              │
    ▼                                                              │
CDN / GeoDNS                                                       │
    │                                                              │
    ▼                                                              │
Load Balancer (L7, rate limiting)                                  │
    │                                                              │
    ▼                                                              │
┌─────────────────────────────────────────┐                        │
│          Stateless API Servers          │                        │
│  ┌────────────┐  ┌───────────────────┐  │                        │
│  │File Service│  │  Block Service    │  │◄── chunk completion ───┘
│  │(metadata)  │  │(dedup, sessions)  │  │
│  └─────┬──────┘  └───────┬───────────┘  │
│        │                 │              │
│  ┌─────┴──────┐  ┌───────┴───────────┐  │
│  │Sync Service│  │  Share Service    │  │
│  └─────┬──────┘  └───────────────────┘  │
└────────┼────────────────────────────────┘
         │
    ┌────┴──────────────────────────────────┐
    │           Message Queue (Kafka)       │
    │  ┌──────────────┐  ┌───────────────┐  │
    │  │ Sync Events  │  │ Index Events  │  │
    │  └──────┬───────┘  └──────┬────────┘  │
    └─────────┼─────────────────┼───────────┘
              │                 │
              ▼                 ▼
    ┌─────────────────┐  ┌──────────────┐
    │WebSocket Gateway│  │Elasticsearch │
    │(real-time push) │  │(file search) │
    └─────────────────┘  └──────────────┘

Storage Layer:
    PostgreSQL (metadata, sharded by user_id)
    Redis Cluster (metadata cache, sessions, folder trees)
    S3 (content blocks, content-addressed)
```

**Upload path:** Client splits file → computes chunk hashes → POST upload-session → server returns missing chunks (dedup!) → client uploads missing chunks via pre-signed S3 URLs → POST complete → server creates file record + version → Kafka event → WebSocket push to other devices.

**Download path:** Client requests download → File Service looks up blocks → returns CDN URL (public/shared) or signed S3 URLs (private) → client downloads blocks in parallel → assembles file locally.

**Sync path:** Device reconnects → GET /sync/delta?cursor=X → server returns all events since X → client applies events → resolves conflicts → updates local state + cursor.

---

## Phase 4 — Deep Dives (15 min)

### 4a. Chunked Upload with Resumability (~4 min)

**Why chunking matters:** A 10 GB file uploaded as a single request fails completely on any network interruption. With 4 MB chunks, the client retries only the failed 4 MB, not the entire 10 GB.

**Chunk size trade-off:**

| Chunk Size | Pros | Cons |
|------------|------|------|
| 1 MB | Fine-grained dedup, fast retry | More HTTP overhead, more metadata per file |
| 4 MB ✅ | Good balance of dedup granularity and overhead | Moderate retry cost |
| 16 MB | Fewer requests, less metadata | Coarser dedup, longer retry on failure |

**Upload flow in detail:**

```
1. Client: split file into 4 MB chunks
2. Client: SHA-256 each chunk → [hash_0, hash_1, ..., hash_N]
3. Client → Server: POST /upload-session {filename, size, hashes[]}
4. Server: check which hashes already exist in block store (dedup!)
5. Server → Client: {sessionId, missingChunks: [2, 5, 7], presignedUrls: [...]}
6. Client: upload chunks 2, 5, 7 in parallel (8 concurrent uploads)
7. Client → Server: POST /upload-session/{id}/complete
8. Server: verify all chunks received, create file record, link blocks
```

**Resumability:** If upload is interrupted, the client calls `GET /upload-session/{id}/status` to learn which chunks were received, then resumes from where it left off. Upload sessions expire after 24 hours.

### 4b. Block-Level Deduplication (~4 min)

**How it works:**

```
Block Storage (content-addressed):
    S3 key = SHA-256 hash of block content
    e.g., s3://blocks/a1b2c3d4e5f6...

Dedup check at upload time:
    Client sends: [hash_0, hash_1, hash_2, hash_3]
    Server checks: hash_0 exists ✓, hash_1 exists ✓, hash_2 NEW, hash_3 exists ✓
    Server returns: "upload only chunk 2" (75% bandwidth saved for this file!)
```

**Cross-user dedup:** If User A and User B both upload the same PDF, the blocks are stored once. Both files' `FILE_BLOCK` entries point to the same `BLOCK` records.

**Reference counting:**
- When a file version references a block: `ref_count++`
- When a file version is deleted: `ref_count--`
- Background GC job: delete blocks where `ref_count = 0` (with a grace period to handle race conditions).

**Savings estimate:** Industry benchmarks (Dropbox, backup services) show 30–50% reduction in stored bytes from block-level dedup. At 500 PB raw, this saves ~200 PB ≈ millions of dollars annually in S3 costs.

### 4c. Sync and Conflict Resolution (~4 min)

**Sync protocol:**

```
Each device maintains:
    sync_cursor: last event sequence number seen

Reconnection:
    Device → Server: GET /sync/delta?cursor=10542
    Server → Device: events 10543–10600 [FileCreated, FileModified, ...]
    Device: apply events in order, update cursor to 10600
```

**Real-time push:** For online devices, the server pushes events via WebSocket immediately — no need to poll.

**Conflict detection:**
```
Device A (offline): edits report.docx (base: v3) → pushes v3→v4
    Server: accepts, current_version now 4 ✓

Device B (offline): edits report.docx (base: v3) → pushes v3→v4
    Server: CONFLICT — expected base v3, but current is v4
```

**Conflict resolution strategy:**

| Scenario | Resolution |
|----------|-----------|
| Different files modified | No conflict — merge both changes |
| Same file, non-overlapping blocks changed | Auto-merge: create new version combining blocks |
| Same file, overlapping blocks changed | Conflict copy: save as "report (Device B's conflict).docx" |
| File deleted on A, modified on B | Keep B's version, notify A |

**Why not last-write-wins?** It silently loses data. A user who spent an hour editing a document would lose their work if another device happened to sync a second later. Conflict copies are visible and recoverable.

### 4d. Metadata at Scale (~3 min)

**The challenge:** 500 billion file records × 1 KB = 500 TB of metadata. This far exceeds a single PostgreSQL instance.

**Sharding strategy:**
```
Shard key: user_id
    shard_id = hash(user_id) % num_shards

Why user_id?
    - Folder listing is per-user: SELECT * FROM files WHERE user_id=? AND folder_id=?
    - All of a user's files are co-located on one shard
    - Avoids cross-shard queries for the most common operation
```

**Shard sizing:** Start with 256 shards. At 500 TB / 256 = ~2 TB per shard — manageable for PostgreSQL with proper indexing.

**Folder tree caching:** Recursive folder queries are expensive. Cache the folder tree per user in Redis (serialized as JSON, TTL 10 min, invalidated on folder change). Most users have < 10,000 folders — this fits in a few KB.

**Read replicas:** Each metadata shard has 2 read replicas for folder listing and search queries. Writes go to the primary. This handles the read-heavy access pattern (browse files ≫ upload files).

---

## Phase 5 — Trade-offs & Wrap-up (5 min)

### Key Trade-offs to Surface

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| Consistency model | Strong for metadata, eventual for sync | Users see correct file list immediately; cross-device sync may lag seconds |
| Chunk size | 4 MB | Smaller = finer dedup + faster retry; larger = less overhead. 4 MB is the industry standard (Dropbox uses this) |
| Dedup level | Block-level, not file-level | More storage savings but higher CPU cost for hashing and more metadata per file |
| Sync model | Push via WebSocket | More complex than polling but delivers real-time sync experience |
| Conflict resolution | Conflict copies (not last-write-wins) | Creates duplicate files but never loses user data |
| Metadata DB | PostgreSQL (sharded) | Gives up easy horizontal scaling of NoSQL; gains strong consistency and transactional guarantees for folder operations |

### Evolution Narrative

| Version | What Changes | Handles |
|---------|-------------|---------|
| **v1-basic** | Single server, direct upload to local disk, simple metadata DB | ~100 users, files < 100 MB |
| **v2-scaled** | S3 for content, chunked uploads, CDN for downloads, Redis metadata cache, basic sync via polling | ~1M users, 10K uploads/sec |
| **v3-distributed** | Sharded PostgreSQL, block-level dedup, WebSocket real-time sync, conflict resolution, multi-region S3 replication, Kafka event pipeline, Elasticsearch for search | 500M users, 11.5K uploads/sec, 500 PB storage |

### Closing Statement (say this to the interviewer)

> "To summarize: we've designed a file storage and sync service for 500M users with 1B daily uploads. The core architecture separates content (S3 block store with 4 MB chunks) from metadata (sharded PostgreSQL). We achieve ~40% storage savings through block-level deduplication with content-addressed hashing. Sync is event-driven — WebSocket push for online devices, delta cursor for reconnecting devices — with conflict copies to prevent data loss. The metadata layer scales via user-based sharding with Redis caching for folder trees. The system evolves from a simple upload service to a globally distributed, petabyte-scale platform. The main open question is whether to invest in real-time collaborative editing, which would require a separate OT/CRDT engine — that's a v4 conversation."

---

*See [RUBRIC](./RUBRIC.md) for how this answer maps to scoring criteria, and [PITFALLS](./PITFALLS.md) for common mistakes to avoid.*
