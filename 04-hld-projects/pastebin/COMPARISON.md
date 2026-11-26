# Pastebin - Comparison

How Pastebin compares to related systems. Understanding these parallels strengthens your ability to discuss trade-offs and reuse patterns across interviews.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Pastebin vs URL Shortener

Both systems map a short ID to an underlying piece of data, but the payload nature fundamentally changes the storage architecture.

| Concern | Pastebin | URL Shortener | Key difference |
|---------|----------|---------------|----------------|
| **Core operation** | Map short code → text blob | Map short code → long URL | Pastebin returns content; Shortener returns a redirect |
| **Response** | `200 OK` + text body (KBs-MBs) | `301/302 Redirect` (~200 bytes) | Pastebin handles heavy payloads |
| **Write payload** | Large text (needs Object Storage) | Tiny string (fits in KV store) | Shortener can use single DB; Pastebin needs DB + S3 |
| **Caching impact** | Moderate (some viral pastes) | Critical (hot redirects) | CDN is crucial for both, but for different payload sizes |
| **Expiration** | Very common (hours/days) | Rare (mostly permanent links) | Pastebin requires aggressive active TTL cleanup |
| **Deduplication** | Difficult (text comparison is expensive) | Easy (hash the long URL) | Shorteners often dedup URLs; Pastebins rarely dedup text |

## Pastebin vs File Storage (e.g., Dropbox / Google Drive)

Pastebin is a simplified file storage system limited to plain text and flat hierarchies.

| Concern | Pastebin | File Storage | Key difference |
|---------|----------|--------------|----------------|
| **Data Types** | Plain text only | Binary files (images, video) | File storage requires chunking, resumable uploads |
| **Hierarchy** | Flat namespace (ID -> Text) | Complex (Folders, nested paths) | File storage needs a complex metadata tree database |
| **Access Control** | Anonymous, public links | Strictly authenticated, ACLs | Pastebin avoids complex identity management |
| **Updates** | Immutable (usually write-once) | Mutable (collaborative editing) | Pastebin has much simpler concurrency requirements |

## Cross-links

- [URL Shortener Design](../url-shortener/)
- [File Storage Design](../file-storage/)
