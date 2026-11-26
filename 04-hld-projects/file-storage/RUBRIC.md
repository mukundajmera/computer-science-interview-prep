# File Storage — Interview Scoring Rubric

A structured rubric for evaluating File Storage system design interviews across 7 dimensions, each scored from 1 (Poor) to 5 (Strong).

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements Gathering | 10% | Clarifying questions, scope definition |
| 2 | Back-of-Envelope Estimation | 10% | Storage, bandwidth, metadata math |
| 3 | API Design | 15% | Upload/download/sync endpoints, chunking |
| 4 | Data Model | 15% | File/block/version schema, indexing |
| 5 | Architecture | 20% | Components, upload/download/sync flows |
| 6 | Deep Dives | 20% | Chunked upload, deduplication, sync conflict resolution, metadata at scale |
| 7 | Trade-offs & Communication | 10% | Pros/cons, justification, clear explanation |

---

## 1. Requirements Gathering

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Jumps into design without clarifying. Misses the distinction between metadata and content storage. Does not ask about file sizes, sync requirements, or sharing model. |
| **3 — Acceptable** | Asks about DAU, average/max file sizes, and whether real-time sync is needed. Identifies core functional requirements (upload, download, sync, share) and mentions availability or storage targets. Separates functional and non-functional requirements. |
| **5 — Strong** | Systematically clarifies scope: 500M users, 100M DAU, 1B daily uploads, average 1 MB files (max 10 GB), 1,000 files/user, multi-device sync, versioning depth, and sharing permission model. Explicitly scopes out real-time collaborative editing and rich media transcoding. Separates functional and non-functional requirements with specific numbers (99.9% availability, strong metadata consistency, eventual content consistency). |

---

## 2. Back-of-Envelope Estimation

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Provides no numbers or wildly inaccurate estimates. Cannot derive upload throughput from daily figures. Skips storage or bandwidth entirely. |
| **3 — Acceptable** | Calculates upload rate (~11,500 files/sec) from 1B daily uploads. Provides rough total storage estimate (order-of-magnitude correct). Mentions metadata storage needs separately from content storage. |
| **5 — Strong** | Derives all key figures methodically: 1B uploads/day → ~11,500 files/sec (peak ~35K/sec). Computes total content storage (500B files × 1 MB avg = 500 PB raw, ~300 PB with dedup). Separates metadata (500B × 1 KB ≈ 500 TB). Estimates upload bandwidth (11,500 × 1 MB ≈ 11.5 GB/s ingress). Calculates chunk count per file (1 MB ÷ 4 MB = 1 chunk for average file; 10 GB ÷ 4 MB = 2,500 chunks for max file). Sizes metadata cache (100M active users × 50 files hot ≈ 5B entries × 200B ≈ 1 TB Redis cluster). |

---

## 3. API Design

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Vague or missing API definition. Treats upload as a simple single-request POST. No mention of chunking, resume, or pre-signed URLs. |
| **3 — Acceptable** | Defines `POST /files/upload-session` to initiate upload, `PUT` for chunk upload, and `GET /files/{id}/download` for download. Mentions pre-signed URLs for direct-to-S3 upload. Includes basic sync and share endpoints. |
| **5 — Strong** | Provides versioned REST endpoints with complete request/response payloads. Covers session creation (201 with missing chunk list), chunk upload via pre-signed URLs, completion (200 with assembled file metadata), download (redirect to CDN/signed URL), sync delta (`GET /sync/delta?cursor=`), and sharing (`POST /shares`). Lists error codes (400, 404, 409 conflict, 413 too large, 429 rate limited). Discusses idempotent chunk uploads and resumable sessions. Mentions WebSocket endpoint for real-time sync notifications. |

---

## 4. Data Model

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No schema defined or describes only a flat file table. No distinction between file metadata and block storage. No discussion of database choice. |
| **3 — Acceptable** | Defines separate File, Block, and FileVersion tables. Chooses a relational DB for metadata with brief rationale. Mentions content-addressable block storage in S3. Includes at least one index (e.g., `user_id + folder_id`). |
| **5 — Strong** | Presents a complete schema: User, Folder, File, FileVersion, Block, FileBlock (junction), Share, Device, SyncCursor, and UploadSession tables. Justifies PostgreSQL for metadata (strong consistency, complex folder queries, transactional version updates) and S3 for block content. Defines partition strategy (`FILE` by `user_id`, `BLOCK` by `content_hash` prefix). Explains content-addressed blocks with `reference_count` for garbage collection. Describes indexes: `FILE(user_id, folder_id, name)` for folder listing, `BLOCK(content_hash)` for dedup, `SYNC_CURSOR(device_id)` for sync state. Discusses soft deletes with TTL-based permanent purge. |

---

## 5. Architecture

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Draws a single box or lists components without showing data flow. No separation of metadata and content paths. Treats upload and download as symmetric operations. |
| **3 — Acceptable** | Shows a layered diagram: clients → load balancer → API servers → metadata DB + S3. Separates upload flow (client → API → S3) and download flow (client → CDN → S3). Mentions a sync service and message queue at a high level. |
| **5 — Strong** | Draws a complete architecture: clients (desktop/mobile/web) → CDN/DNS → load balancer with rate limiting → stateless API servers → File Service + Block Service + Sync Service + Share Service. Storage layer: PostgreSQL (metadata) + S3 (blocks) + Redis (metadata cache, upload sessions, folder tree). Async pipeline: Kafka for sync events and search indexing → Elasticsearch. Real-time layer: WebSocket gateway for device sync push. Separates upload flow (session → dedup check → pre-signed URL → direct S3 upload → completion → Kafka event → sync push), download flow (metadata lookup → CDN redirect or signed URL → parallel block fetch), and sync flow (delta cursor → event stream → conflict resolution → push). |

---

## 6. Deep Dives

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Cannot explain chunked uploads or why they matter. No mention of deduplication, sync conflicts, or metadata scaling. Treats the system as a simple file server. |
| **3 — Acceptable** | Describes chunked upload with a fixed chunk size and parallel upload. Mentions content-hash dedup at the block level. Aware of sync conflicts but offers only surface-level mitigation (e.g., "last-write-wins"). Knows metadata needs a relational DB but doesn't address scale. |
| **5 — Strong** | **Chunked upload:** Explains 4 MB chunk size trade-off, pre-signed URL pattern for direct-to-S3, upload session tracking, resumability on failure (client retries only failed chunks), checksum verification per chunk. **Deduplication:** Content-addressable storage with SHA-256 per block; dedup check before upload returns only missing chunks; cross-user dedup with reference counting; estimates 30–40% savings. **Sync conflict resolution:** Version vector or sequence-number based conflict detection; auto-merge for non-overlapping changes; conflict copy creation ("filename (conflict).ext") for true conflicts; CRDT consideration for advanced merge. **Metadata at scale:** PostgreSQL sharded by `user_id`; folder tree caching in Redis; pagination for large folders; async search indexing via Kafka → Elasticsearch; discusses hot user problem and read replica strategy. |

---

## 7. Trade-offs & Communication

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Makes design choices without explaining why. Cannot articulate alternatives or downsides. Answers are disorganized and hard to follow. |
| **3 — Acceptable** | Explains at least two trade-offs (e.g., strong vs eventual consistency for metadata, chunk size selection). Communicates the design in a logical order. Responds to interviewer follow-ups adequately. |
| **5 — Strong** | Proactively surfaces trade-offs at each decision point: strong consistency for metadata vs eventual for content (chose strong metadata for user-visible correctness), chunk size 4 MB (smaller = more overhead, larger = slower retry), block-level vs file-level dedup (block saves more but adds complexity), push vs pull sync (chose push via WebSocket for real-time feel). Articulates the evolution path (v1 single upload → v2 chunked + CDN → v3 multi-region dedup + real-time sync). Communicates clearly, uses diagrams, and structures the answer with time awareness. Wraps up by summarizing key decisions and open questions. |

---

## Quick Calibration Guide

| Total Score (out of 35) | Rating | Recommendation |
|--------------------------|--------|----------------|
| 30–35 | 🟢 Strong Hire | Exceeds expectations across all dimensions |
| 22–29 | 🟡 Hire | Solid fundamentals, minor gaps in depth |
| 15–21 | 🟠 Lean No Hire | Acceptable basics but missing key deep dives |
| 7–14 | 🔴 No Hire | Significant gaps in design thinking |

---

*Use this rubric alongside the [STRONG-ANSWER](./STRONG-ANSWER.md) for calibration and [PITFALLS](./PITFALLS.md) to identify common failure modes.*
