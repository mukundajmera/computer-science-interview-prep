# File Storage Service

## Problem Statement

Design a cloud file storage service for upload, download, sharing, and multi-device sync with efficient large-file transfer and metadata correctness.

---

## Requirements and Constraints

### Functional Requirements

1. Upload files from any device.
2. Download files from any device.
3. Share files/folders using controlled links.
4. Sync file changes across signed-in devices.
5. Support resumable chunk uploads for large files.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.9% |
| Upload session init latency | < 300 ms P99 |
| Small-file download latency | < 500 ms P99 |
| Metadata consistency | Strong |
| Content consistency | Eventual acceptable |
| Scale | PB-level content storage |

### Capacity Assumptions

- 100M DAU.
- 1B uploads/day.
- Avg file size 1 MB, max 10+ GB.
- Read-heavy with bursty enterprise sync patterns.

### Out of Scope

- Real-time collaborative editing engine internals.
- Full media transcoding/preview pipelines.
- Enterprise DLP/compliance suites.

### Scaling Pattern Constraints

- **Read scaling trigger:** PB-level sync storms require segmented read recomputation paths and cached metadata per [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/), keeping metadata DB replicas healthy during batch sync sweeps.
- **Write scaling trigger:** 1B uploads/day with multi-GB files demand adaptive partitioning, burst smoothing, and batching (see [03-hld-concepts/write-scaling](../../03-hld-concepts/write-scaling/)) so the upload session service never blocks other tenants.
- **Large blob handling:** Chunked uploads, resumability, and tiered storage from [03-hld-concepts/large-blob-handling](../../03-hld-concepts/large-blob-handling/) prevent timeouts and keep the chunk transfer service stable.
- **Long-running tasks:** Background cleanup (e.g., dedup, virus scan, GC) should be tracked with leases, retries, and dead-letter queues per [03-hld-concepts/long-running-tasks](../../03-hld-concepts/long-running-tasks/) so they execute independently of user-facing APIs.

---

## High-Level Design Outline

### Core Services

- File Metadata Service
- Upload Session Service
- Chunk Transfer Service
- Sync Event Service
- Sharing/Permission Service

### Storage Model

- Metadata DB for files/folders/versions.
- Object store for file chunks or multipart objects.
- Redis cache for hot metadata and sync cursors.
- Queue/stream for sync propagation.

### API Surface (Illustrative)

```http
POST /api/v1/uploads/sessions
PUT /api/v1/uploads/sessions/{sessionId}/chunks/{chunkId}
POST /api/v1/uploads/sessions/{sessionId}/complete
GET /api/v1/files/{fileId}/download
GET /api/v1/sync/delta?cursor=...
```

---

## Scoring Rubric

Strong answers should clearly explain:

1. Chunked/resumable upload protocol.
2. Sync cursor and conflict behavior.
3. Metadata/content consistency separation.
4. Cost control (dedup/tiering) as extension.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Single-shot upload assumptions for large files.
- No sync cursor model.
- Treating metadata and content as one consistency domain.
- Missing idempotent upload completion.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- Selective sync and smart placeholders?
- Cross-region durability and disaster recovery?
- Cost optimization via dedup and tiering?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Version history policies by account tier.
- Malware scanning pipeline.
- Team collaboration workspace semantics.

---

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/cdn](../../03-hld-concepts/cdn/)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
- [03-hld-concepts/message-queues](../../03-hld-concepts/message-queues/)
- [04-hld-projects/url-shortener](../url-shortener/)
