# File Storage — System Comparison

How the File Storage service compares to related systems: an object storage system (S3), a content delivery network, and a collaboration platform (Google Docs). Understanding these parallels strengthens your ability to discuss trade-offs and reuse patterns across interviews.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## File Storage vs Object Storage (S3)

Object storage (like AWS S3) provides raw blob storage with a flat namespace. A file storage service *uses* object storage as a building block but adds metadata management, folder hierarchy, sync, sharing, and versioning on top.

| Dimension | File Storage (Dropbox/Drive) | Object Storage (S3) | Key Difference |
|-----------|------------------------------|---------------------|----------------|
| **Data model** | Hierarchical folders + files + metadata + versions | Flat namespace: bucket → key → blob | File storage adds folder trees, user ownership, and version history |
| **Access pattern** | Multi-device sync, real-time notifications, file browsing | Direct PUT/GET by key, no sync concept | File storage requires push-based sync; S3 is pull-only |
| **Users** | End users (consumers, teams) with GUI clients | Developers via API; no end-user interface | File storage wraps S3 with a user-facing product layer |
| **Deduplication** | Block-level dedup across users (content-addressed) | No built-in dedup; each PUT stores a full object | File storage reduces costs by deduplicating blocks before writing to S3 |
| **Upload model** | Chunked uploads with resumability, delta sync | Single PUT or S3 Multipart Upload (developer-managed) | File storage orchestrates chunking, dedup, and session tracking on behalf of the client |
| **Versioning** | Application-managed: version table, block sharing, configurable retention | S3 Versioning: keeps every object version, no cross-object dedup | File storage versions share blocks; S3 versions are full copies |
| **Consistency** | Strong for metadata, eventual for cross-device sync | Strong read-after-write (since 2020) | File storage has a more complex consistency model spanning metadata + content + sync |
| **Sharing** | Link sharing, email invites, permission levels (view/edit) | IAM policies, pre-signed URLs, bucket policies | File storage provides user-friendly sharing; S3 provides infrastructure-level access control |

### Shared Patterns

- Both store **binary blobs** as the core data type.
- Both use **content hashing** for integrity verification (ETags in S3, SHA-256 in file storage).
- Both benefit from **lifecycle policies** to tier data between hot and cold storage.

---

## File Storage vs Content Delivery Network (CDN)

A CDN (like CloudFront or Akamai) distributes and caches content at global edge locations for fast delivery. A file storage service uses CDN for download acceleration, but the core problems are fundamentally different.

| Dimension | File Storage (Dropbox/Drive) | CDN (CloudFront/Akamai) | Key Difference |
|-----------|------------------------------|------------------------|----------------|
| **Core function** | Store, sync, and manage user files | Cache and deliver content from edge locations | File storage is a *source of truth*; CDN is a *cache layer* |
| **Data lifecycle** | Files are uploaded, versioned, synced, and eventually deleted by users | Content is cached automatically and evicted by TTL/LRU | File storage manages the full lifecycle; CDN only manages cache residency |
| **Write path** | Complex: chunked upload → dedup → store → sync | No write path; content is pulled from origin on cache miss | CDN has no upload concept — it only accelerates reads |
| **Consistency** | Must be strongly consistent for metadata; user expects to see the file they just uploaded | Eventually consistent by design; stale cache is expected and acceptable | File storage requires correctness; CDN trades freshness for speed |
| **Scale metric** | Total storage (PBs), files managed (billions) | Bandwidth (Tbps), edge PoPs (hundreds), cache hit rate (%) | File storage scales by storage capacity; CDN scales by bandwidth and geographic coverage |
| **Personalization** | Every user sees their own files; access-controlled | Same content served to all requestors (public cache) | CDN assumes shared content; file storage assumes private, per-user content |
| **Latency target** | < 500 ms for small file download; seconds for large files | < 50 ms for cached content at edge | CDN targets ultra-low latency for cached assets; file storage tolerates higher latency for personalized content |
| **Cost driver** | Storage (PBs of S3) + metadata infra (DB, Redis) | Bandwidth (egress from edge PoPs) + origin pull | File storage cost is storage-dominated; CDN cost is bandwidth-dominated |

### Shared Patterns

- Both serve **file content to users over HTTP/HTTPS**.
- Both use **geographic distribution** to reduce latency.
- Both benefit from **caching** — CDN caches at edge; file storage caches metadata in Redis and leverages CDN for shared/public file downloads.

---

## File Storage vs Collaboration Platform (Google Docs)

A collaboration platform enables multiple users to edit the same document simultaneously in real time. A file storage service focuses on storing and syncing files across devices, with editing happening in external applications.

| Dimension | File Storage (Dropbox/Drive) | Collaboration Platform (Google Docs) | Key Difference |
|-----------|------------------------------|--------------------------------------|----------------|
| **Core function** | Store, sync, and share files of any type | Real-time collaborative editing of documents | File storage is format-agnostic; collaboration platform is format-specific (docs, sheets, slides) |
| **Edit model** | Files edited locally in native apps (Word, Photoshop); synced after save | Edits happen in-browser; every keystroke is synchronized | File storage syncs *files*; collaboration platform syncs *operations* |
| **Conflict resolution** | Detect after the fact; create conflict copies | Prevent in real time using OT or CRDTs | File storage resolves conflicts *after* they occur; collaboration platforms prevent them from occurring |
| **Granularity** | File-level or block-level (4 MB chunks) | Character-level or operation-level | Collaboration platforms operate at orders-of-magnitude finer granularity |
| **Latency tolerance** | Seconds to minutes for sync is acceptable | < 100 ms for operation broadcast is required | Collaboration needs real-time; file storage needs reliability |
| **Offline support** | First-class: edit offline, sync on reconnect | Limited: offline edits possible but merge on reconnect is complex | File storage was designed for offline-first; collaboration platforms are online-first |
| **File types** | Any binary or text file | Structured documents (text, spreadsheets, presentations) | File storage handles JPEG, ZIP, MP4, EXE — anything. Collaboration platforms only handle their own formats |
| **Architecture** | Upload → Block Store + Metadata DB + Sync Service | WebSocket → OT/CRDT Engine → Operation Log → Periodic snapshot | Collaboration adds a real-time operation engine that file storage doesn't need |
| **Versioning** | Periodic snapshots (on each save/sync) | Continuous operation history; any point in time is recoverable | Collaboration platforms have richer version granularity but higher storage overhead per document |

### Shared Patterns

- Both need **user authentication and authorization** with fine-grained sharing permissions.
- Both have a **versioning system** (though at different granularities).
- Both must handle **concurrent access** — file storage at the file level, collaboration at the character level.
- Both use **WebSocket connections** for push notifications (sync events vs operation broadcast).

---

## Cross-Cutting Comparison Summary

| Concern | File Storage | Object Storage (S3) | CDN | Collaboration Platform |
|---------|-------------|---------------------|-----|----------------------|
| **Data size per entry** | KB to 10 GB | Bytes to 5 TB | Varies (cached origin content) | KB (document state) |
| **Read/write ratio** | 3:1 (sync-heavy) | Varies by workload | 1000:1+ (read-dominated) | 50:1 (ops-heavy reads) |
| **Primary storage** | S3 (blocks) + PostgreSQL (metadata) | Flat blob store | Edge cache (RAM/SSD) | Operation log + snapshots |
| **Caching importance** | Critical for metadata | Built-in (S3 caches internally) | Caching *is* the product | Critical for operation replay |
| **Consistency model** | Strong (metadata), eventual (sync) | Strong read-after-write | Eventually consistent (TTL) | Strong (OT/CRDT guarantees convergence) |
| **Latency target** | < 500 ms (metadata), seconds (content) | < 100 ms (single object GET) | < 50 ms (edge cache hit) | < 100 ms (operation broadcast) |
| **Primary challenge** | Sync, dedup, metadata at scale | Durability, availability, cost | Cache hit ratio, invalidation, origin shielding | Real-time consistency, OT/CRDT correctness |

---

## When to Reference These Comparisons

- **S3 comes up?** Explain that your file storage *sits on top of* S3 — it adds the user-facing layer (folders, sync, sharing, dedup) that S3 doesn't provide.
- **CDN comes up?** Highlight that CDN is a delivery optimization within your file storage architecture; the hard problems (upload, sync, dedup, metadata) are upstream of the CDN.
- **Google Docs comes up?** Explain that real-time collaboration is a fundamentally different problem (operation-level sync vs file-level sync) that requires a separate OT/CRDT engine, but can integrate with file storage for persistence.

---

*See [DESIGN](./DESIGN.md) for the full File Storage architecture and [FOLLOW-UPS](./FOLLOW-UPS.md) for interview extensions that push toward these related systems.*
