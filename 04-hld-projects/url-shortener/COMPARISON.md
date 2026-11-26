# URL Shortener — System Comparison

How the URL Shortener compares to related systems: Pastebin, a file-sharing service, and DNS. Understanding these parallels strengthens your ability to discuss trade-offs and reuse patterns across interviews.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## URL Shortener vs Pastebin

Pastebin stores and retrieves text content; URL Shortener stores a mapping and immediately redirects. Both are key-value systems, but the read pattern and payload size differ significantly.

| Dimension | URL Shortener | Pastebin | Key Difference |
|-----------|--------------|----------|----------------|
| **Core operation** | Map short code → long URL, return redirect | Map paste ID → text blob, return content | Shortener returns a *redirect*; Pastebin returns *content* |
| **Read response** | `301`/`302` redirect (~200 bytes) | `200 OK` with full text body (up to MBs) | Shortener responses are tiny and cacheable; Pastebin responses can be large |
| **Write payload** | Small (~200 bytes: long URL + metadata) | Large (text content, up to 10 MB) | Pastebin needs object/blob storage; shortener fits in a key-value store |
| **Read/write ratio** | 100:1 (read-heavy) | 5:1 (moderate read-heavy) | Shortener has extreme read skew; Pastebin is more balanced |
| **Caching value** | Very high — hot URLs serve millions of identical redirects | Moderate — pastes are less frequently re-read | CDN caching is critical for shortener; less impactful for Pastebin |
| **Storage engine** | Key-value store (DynamoDB, Cassandra) | Object store (S3) + metadata DB | Pastebin separates metadata from content; shortener stores everything in one table |
| **ID generation** | Must be URL-safe, short (7 chars) | Can be longer, less visibility pressure | Both need unique IDs, but shortener codes appear in every URL users share |
| **Expiration** | Optional, most URLs are permanent | Common, many pastes are temporary | Pastebin has more aggressive cleanup requirements |

### Shared Patterns

- Both use a **unique ID → content** mapping as their core abstraction.
- Both benefit from **CDN edge caching** for popular entries.
- Both can use a **Key Generation Service** for collision-free IDs.

---

## URL Shortener vs File-Sharing Service

A file-sharing service (e.g., Dropbox, WeTransfer) stores and delivers binary files. Both generate shareable links, but the data sizes, upload/download patterns, and storage costs differ dramatically.

| Dimension | URL Shortener | File-Sharing Service | Key Difference |
|-----------|--------------|---------------------|----------------|
| **Stored data** | Metadata only (~160 bytes per URL) | Binary files (KB to GB per file) | File service needs blob storage (S3); shortener fits in a database |
| **Upload size** | Trivial (~200 bytes) | Large (multi-part uploads, up to GBs) | File service needs chunked uploads, resumability, checksums |
| **Download pattern** | Instant redirect (no content transfer from origin) | Full file download (bandwidth-intensive) | Shortener is metadata-only at the application layer; file service transfers heavy payloads |
| **Storage cost** | ~1 TB for 6 billion URLs over 5 years | PBs of storage for millions of files | File service storage cost dominates; shortener cost is compute-dominated |
| **Bandwidth** | Low (~2 MB/s outgoing for redirects) | Very high (GBs/s for concurrent downloads) | File service needs CDN and edge caching far more aggressively for *content delivery* |
| **Write path complexity** | Simple single-row insert | Chunked upload → reassemble → virus scan → store | File service write path is orders of magnitude more complex |
| **Deduplication** | Optional (same long URL → same short code) | Critical (content-based dedup saves PBs) | File service uses content hashing (SHA-256) for dedup; shortener dedup is a nice-to-have |
| **Access control** | Mostly public (anyone with the link) | Often private (owner, shared users) | File service needs robust ACLs and authentication; shortener is usually open |

### Shared Patterns

- Both generate **shareable links** as the primary user-facing output.
- Both benefit from **CDN distribution** (shortener for redirects, file service for content).
- Both need to handle **expiration and cleanup** of old entries.

---

## URL Shortener vs DNS

DNS maps domain names to IP addresses; URL Shortener maps short codes to long URLs. The mapping concept is similar, but scale, update frequency, and caching semantics differ.

| Dimension | URL Shortener | DNS | Key Difference |
|-----------|--------------|-----|----------------|
| **Mapping** | Short code → long URL (application-layer) | Domain name → IP address (network-layer) | DNS operates at the infrastructure layer; shortener is an application service |
| **Scale** | Billions of entries, thousands of lookups/sec | Millions of zones, *trillions* of lookups/day globally | DNS operates at internet-scale with a hierarchical delegation model |
| **Update frequency** | Write-once, rarely updated | Records change infrequently but TTLs vary (minutes to days) | Both are read-heavy, but DNS has a formalized TTL-based propagation model |
| **Caching model** | Application-managed (Redis, CDN) | Built into the protocol (recursive resolvers, stub resolvers, browser cache) | DNS caching is decentralized and hierarchical; shortener caching is centralized |
| **Hierarchy** | Flat namespace (short code is a single key) | Hierarchical (root → TLD → authoritative → record) | DNS resolution traverses multiple levels; shortener is a single-hop lookup |
| **Consistency** | Eventual consistency (acceptable) | Eventual consistency (TTL-based propagation) | Both tolerate stale reads; DNS propagation delays are well-understood |
| **Failure impact** | Broken links for one service | Entire domains become unreachable | DNS failures have far broader blast radius |
| **Protocol** | HTTP/HTTPS | DNS protocol (UDP/TCP port 53) | Different transport and encoding; DNS uses its own binary wire format |

### Shared Patterns

- Both are fundamentally **lookup services**: given a key, return a value.
- Both are **read-heavy** with high cache hit rates.
- Both rely on **TTL-based caching** to balance freshness and performance.
- Both must be **highly available** — downtime breaks dependent services.

---

## Cross-Cutting Comparison Summary

| Concern | URL Shortener | Pastebin | File-Sharing | DNS |
|---------|--------------|----------|-------------|-----|
| **Data size per entry** | ~160 B | Up to 10 MB | Up to GBs | ~100 B |
| **Read/write ratio** | 100:1 | 5:1 | 2:1 | 10,000:1+ |
| **Primary storage** | Key-value DB | Object store + DB | Blob store + DB | Zone files / distributed DB |
| **Caching importance** | Critical | Moderate | Critical for delivery | Critical (built into protocol) |
| **ID/key generation** | Base62, KGS | UUID/hash | Content hash (SHA-256) | Hierarchical naming |
| **Latency target** | < 100 ms | < 500 ms | Seconds (for large files) | < 50 ms |
| **Primary challenge** | Hot keys, collision-free IDs | Large content storage | Bandwidth, chunked uploads | Hierarchical resolution, DDoS |

---

## When to Reference These Comparisons

- **Pastebin comes up?** Reuse your URL Shortener design but swap the redirect response for content retrieval and add object storage.
- **File-sharing comes up?** The link-generation piece is identical; the hard part shifts to upload/download, chunking, and dedup.
- **DNS comes up?** Highlight that your URL shortener is a *simplified, application-level DNS* — same lookup pattern, but without hierarchical delegation.

---

*See [DESIGN](./DESIGN.md) for the full URL Shortener architecture and [FOLLOW-UPS](./FOLLOW-UPS.md) for interview extensions that push toward these related systems.*
