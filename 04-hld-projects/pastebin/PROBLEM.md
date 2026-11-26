# Pastebin

## Problem Statement

Design a Pastebin-like service that allows users to store plain text and share it via a unique short URL. The system needs to support high read volume, optional expiration times, and guard against abuse.

---

## Requirements and Constraints

### Functional Requirements

1. Create paste with a text block and return a unique 7-character short link.
2. View paste contents via the short link.
3. Configurable expiration (1 hour, 1 day, 1 month, or never).
4. IP-based token-bucket rate limiting to mitigate spam.
5. Active and passive TTL cleanup of expired pastes.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Read latency | < 50 ms P99 |
| Availability | 99.99% |
| Read/Write ratio | 10:1 to 100:1 |
| Scale | 10M writes/month, 100M reads/month |
| Storage | 12.7 GB/month, 450 GB over 3 years |

### Capacity Assumptions

- 10M writes/month ≈ 4 writes/sec avg (peak ≈ 50 writes/sec).
- 100M reads/month ≈ 40 reads/sec avg (peak ≈ 500 reads/sec).
- Size per paste: 1 KB text + 270 bytes metadata ≈ 1.27 KB.
- Monthly storage: 10M × 1.27 KB = 12.7 GB/month. 3 Years ≈ 450 GB.
- Key space: 7 Base62 chars = 62^7 ≈ 3.52 trillion unique keys (well exceeds 360M required over 3 years).

### Out of Scope

- User accounts and authentication.
- Syntax highlighting implementation details (mostly frontend).
- Editing or updating a paste after creation.

---

## High-Level Design Outline

### Core Services

- API Gateway with Token-Bucket Rate Limiter (IP-based).
- Paste Creation Service.
- Paste Read Service.
- Key Generation Service (Pre-generated Base62 keys).
- Background Sweeper (Active TTL cleanup).

### Storage and Cache

- SQL Database for metadata (keys, expiration, sizes, blob paths).
- S3/Object Storage for text blobs (paths: `s3://pastebin-blobs/{year}/{month}/{short_key}.txt`).
- Redis Cache for read performance (Key: `paste:{short_key}` -> Value: raw text content, TTL aligned with expiration).

### API Surface (Illustrative)

```http
POST /api/v1/pastes
GET /api/v1/pastes/{shortCode}
```

---

## Scoring Rubric

Strong answers explicitly cover:

1. Trade-offs of metadata vs text payload storage (separation of concerns).
2. Key generation strategy (Base62 Hash Truncation vs Key Generation Service).
3. Lifecycle management of pastes (Passive vs Active TTL cleanup).
4. Sub-millisecond read optimization utilizing CDN/Redis.

See [RUBRIC](./RUBRIC.md).

---

## Common Pitfalls

- Storing large multi-kilobyte text blobs directly in SQL database buffer pools.
- Relying solely on passive expiration, leading to permanent disk space leaks.
- Using hash truncation without handling collision retries appropriately.

See [PITFALLS](./PITFALLS.md).

---

## Follow-Up Questions

- How do you handle a viral paste accessed millions of times per hour?
- How would you enforce compliance (e.g. DMCA takedown requests) or abuse scanning?
- What changes if we need end-to-end encryption?

See [FOLLOW-UPS](./FOLLOW-UPS.md).

---

## Variants and Extensions

- Secure pastes with passwords.
- "Burn after reading" one-time use links.
- Image/binary file support.

---

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [04-hld-projects/url-shortener](../url-shortener/)
- [03-hld-concepts/caching](../../03-hld-concepts/caching/)
