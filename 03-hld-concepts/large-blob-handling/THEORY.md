# Large Blob Handling

Large blob handling is the pattern for transferring and serving large files (images, videos, documents) without routing bulk bytes through application servers.

## What is it?

The system issues short-lived, scoped upload/download credentials so clients talk directly to object storage and CDN edges, while the application controls authorization and metadata.

## Why do we need it?

- Proxying large files through API servers wastes compute and bandwidth.
- Large transfers fail frequently on unstable networks if not resumable.
- Metadata state can drift from object-store state without reconciliation.

## Core strategy progression

1. Keep metadata in primary DB, bytes in object storage.
2. Use signed or presigned URLs for direct upload/download.
3. Use multipart/chunked transfer for resumability.
4. Sync DB state from storage events, with periodic reconciliation jobs.
5. Serve downloads through CDN with range request support.

## Requirements and constraints

- File-size threshold for direct upload path (for example >10MB).
- Upload session TTL and resumability window.
- Validation policy (type/size/checksum/quarantine).
- Metadata consistency and completion semantics.
- Download performance targets and geo coverage.

## Scoring rubric

| Dimension | Strong signal | Weak signal |
|---|---|---|
| Data path design | Direct-to-storage, server as control plane | API proxy for all blob traffic |
| Resumability | Multipart + missing-chunk resume | Restart whole upload on failure |
| State consistency | Event-driven updates + reconciliation | Trusts client completion blindly |
| Abuse controls | Quarantine, scanning, limits, signed scope | No upload constraints |

## Common pitfalls

- Storing large binaries directly in relational tables.
- Over-permissive signed URLs (size/type not constrained).
- Missing cleanup for abandoned multipart uploads.
- Treating client completion as source of truth.
- Ignoring range requests for large downloads.

## Follow-up questions

1. What happens if upload fails at 99%?
2. How do you prevent malicious file abuse?
3. How do you keep metadata and object state aligned?
4. When should you not use direct upload?
5. How do you optimize global download latency?

## Variants and extensions

- **Compliance-heavy flows:** proxy + inspection pipelines.
- **High-trust internal tools:** simpler signed URL policies.
- **Media platforms:** multipart upload + async transcoding.
- **Enterprise storage:** stronger metadata governance and retention controls.

## Related concepts

- [Caching](../caching/THEORY.md)
- [Database Replication](../database-replication/THEORY.md)
- [Database Sharding](../database-sharding/THEORY.md)
- [Message Queues](../message-queues/THEORY.md)
- [CDN](../cdn/THEORY.md)

## Related projects

- [File Storage](../../04-hld-projects/file-storage/)
- [Video Streaming](../../04-hld-projects/video-streaming/)
- [News Feed](../../04-hld-projects/news-feed/)
