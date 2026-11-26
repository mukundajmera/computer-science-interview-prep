# 📋 Pastebin Design

Use this template as a framework for practicing system design interviews.

---

## 1. 📝 Requirements and Constraints

### Problem Statement
- System to design: Pastebin
- Core user value: A service that allows users to quickly store plain text and share it via a unique short URL.

### Functional Requirements
- [x] FR1: Create paste with a text block and return a unique 7-character short link.
- [x] FR2: View paste contents via the short link.
- [x] FR3: Configurable expiration (1 hour, 1 day, 1 month, or never).
- [x] FR4: IP-based token-bucket rate limiting to mitigate spam.
- [x] FR5: Active and passive TTL cleanup of expired pastes.

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Read latency | < 50 ms P99 |
| Write latency | < 200 ms P99 |
| Throughput | 10M writes/month, 100M reads/month |
| Consistency | Eventual consistency is acceptable |
| Durability | No data loss before expiration |

### Constraints
- Read-heavy system (10:1 to 100:1 ratio).
- Cost preference: Minimize storage costs for expired data.

### Out of Scope
- User accounts and authentication.
- Syntax highlighting implementation details.
- Editing or updating a paste after creation.

---

## 2. 📊 Back-of-Envelope Estimation (Only What Changes Design)

### Traffic

| Metric | Value | Formula |
|---|---|---|
| Writes/month | 10M | input |
| Reads/month | 100M | input |
| Avg Write QPS | ~4 | 10M / (30 * 86400) |
| Peak Write QPS | ~50 | Avg * 10 |
| Avg Read QPS | ~40 | 100M / (30 * 86400) |
| Peak Read QPS | ~500 | Avg * 10 |

### Storage

| Data Type | Avg Size | Daily Volume | 1-Year |
|---|---|---|---|
| Paste metadata | 270 B | ~90 MB | ~32 GB |
| Paste text blob | 1 KB | ~333 MB | ~118 GB |
| Total | 1.27 KB | ~423 MB | ~150 GB (450GB 3-yr) |

### Decision Notes
- **Which estimate forces a design choice?** Storage size vs DB buffer cache: 1KB average paste size means storing it directly in the DB could pollute the DB's buffer cache, leading to poor read performance for metadata. Thus, separate metadata (DB) from text blobs (Object Storage).
- **Key space:** 7 Base62 chars = 62^7 ≈ 3.52 trillion unique keys. This safely handles 120M keys/year without exhausting the keyspace.

---

## 3. 🔌 API / System Interface

### External Contract
- Protocol choice: REST over HTTPS.
- Auth model: Unauthenticated (anonymous).
- Rate limiting policy: IP-based token bucket (e.g., max 10 requests per minute).

### Core Endpoints

```http
POST /api/v1/pastes
{
    "text": "Hello world",
    "expiration": 3600,
    "custom_alias": "hello-world"
}
```

```http
GET /api/v1/pastes/{shortCode}
```

### Error Model
- `400` Invalid input (e.g., text too large)
- `404` Paste not found (or expired)
- `409` Custom alias already taken
- `429` Throttled by rate limiter
- `5xx` Internal dependency failure

---

## 4. 🗄️ Core Entities and Data Model

### Storage Choices
- **Primary DB (Metadata):** SQL (PostgreSQL or MySQL) or NoSQL (DynamoDB/Cassandra). We'll use **SQL** for relational guarantees on custom alias uniqueness, though NoSQL scales better horizontally.
- **Object Storage (Blobs):** Amazon S3 (or equivalent) for raw text storage to keep DB slim.
- **Cache:** Redis for read-heavy paste text, TTL aligned with paste expiration.

### Core Entities

```sql
CREATE TABLE pastes (
    short_key VARCHAR(7) PRIMARY KEY,
    custom_alias VARCHAR(30) UNIQUE,
    paste_path VARCHAR(255) NOT NULL,
    size_bytes INT NOT NULL,
    expiration_timestamp TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    user_ip VARCHAR(45) NOT NULL,
    INDEX idx_expiration (expiration_timestamp)
);
```

**Blob storage layout:** `s3://pastebin-blobs/{year}/{month}/{short_key}.txt`
**Redis Cache:** Key: `paste:{short_key}` -> Value: raw text content, TTL aligned with expiration

### Key Access Patterns
1. **Read path query:** Lookup metadata by `short_key`, fetch blob from cache or S3.
2. **Write path mutation:** Get unique `short_key`, upload blob to S3, insert metadata.
3. **Cleanup:** Query `WHERE expiration_timestamp < NOW()`.

### Partition and Index Notes
- **Partition key:** `short_key`.
- **Hot key risk:** Viral pastes (mitigated via CDN/Redis).
- **Required indexes:** `expiration_timestamp` for active cleanup sweeps.

---

## 5. 🏗️ High-Level Architecture

### Component List
- CDN (Cloudflare/CloudFront)
- API Gateway / Load Balancer
- Stateless API servers (Write/Read nodes)
- Rate Limiter (Redis-backed)
- Key Generation Service (KGS)
- SQL DB (Metadata)
- S3 (Blob Storage)
- Redis (Text Cache)
- Background Sweeper (Cron/Workers)

### Read Path
1. Client requests `/{shortCode}`.
2. CDN checks edge cache; returns if hit.
3. API Gateway routes to Read Service.
4. Read Service checks Redis cache: `GET paste:{shortCode}`.
5. On cache miss: Query SQL DB for metadata -> fetch blob from S3 -> store in Redis -> return.

### Write Path
1. Client POSTs text to `/api/v1/pastes`.
2. API Gateway applies IP rate limiting.
3. Write Service requests unique key from KGS.
4. Write Service uploads text to S3 (`s3://.../{shortCode}.txt`).
5. Write Service inserts metadata into SQL DB.
6. Return `shortCode` to client.

### Failure-aware Path
- **S3 Failure:** Return 503 if S3 upload fails. Retries can be done on the client.
- **Redis Failure:** Gracefully degrade to querying S3 + DB (with reduced performance).

---

## 6. 🔍 Deep Dives (Pick 1-2)

### Deep Dive A: Key Generation Service (KGS) vs Hash Truncation
- **Bottleneck:** Generating unique 7-char IDs at scale without DB write collisions.
- **Alternative considered:** MD5 Hash Truncation (`Base62(MD5(ip + ts))[:7]`). Requires retries if the truncated hash collides.
- **Chosen pattern:** Key Generation Service (KGS). KGS pre-generates millions of random Base62 IDs, stores them in a DB, and hands them out in batches to API servers.
- **Trade-off accepted:** KGS is a single point of failure and adds complexity, but guarantees 0 collisions at write-time, enabling blazing fast $O(1)$ writes.

### Deep Dive B: Passive vs Active TTL Cleanup
- **Bottleneck:** Expired pastes waste S3 and DB storage.
- **Alternative considered:** Passive deletion. Only delete when a user tries to access an expired paste (returns 404, triggers cleanup).
- **Chosen pattern:** Hybrid approach. Passive deletion + Active TTL Sweeper. Sweeper runs a cron job querying `WHERE expiration_timestamp < NOW() LIMIT 1000`, queuing tasks to delete from DB and S3.
- **Trade-off accepted:** Background sweepers add operational overhead and DB read load, but guarantee that "abandoned" pastes are deleted, saving long-term disk costs.

---

## 7. ⚖️ Trade-offs and Decisions

| Decision | Option Chosen | Alternative | Why Chosen Now | Revisit Trigger |
|---|---|---|---|---|
| Text Storage | S3 Object Store | SQL Database (BLOB) | Keeps DB lean and fast | Text size drops < 256B |
| Key Generation | KGS (Pre-gen) | On-the-fly hash truncation | Fast writes, no collision retries | Write QPS drops low |
| Cleanup Strategy| Active + Passive | Passive only | Saves long-term storage costs | Storage costs become free |

---

## 8. 🔮 Follow-up Questions

1. **What changes at 10x scale?** DB needs sharding by `short_key`. S3 remains fine, but we might need multi-region CDN and read replicas.
2. **How to handle a viral paste (1M requests/min)?** Edge caching at the CDN level is critical. If CDN is bypassed, an in-memory local cache on API servers avoids overwhelming Redis.
3. **How do you support end-to-end encryption?** Clients encrypt text locally. Server stores ciphertext. Decryption key is embedded in the URL fragment (`domain.com/abc#key`), which never hits the server.

---

## 9. 🧩 Variants and Extensions

- **Variant 1 (Private Pastes):** Require passwords. Store bcrypt hash of password in DB, prompt user before decrypting/showing content.
- **Variant 2 (Burn after reading):** Delete paste immediately upon first read. Requires atomic read-and-delete operations (e.g., using Redis `GETDEL` or DB transaction).
- **Variant 3 (Syntax highlighting):** Store the language tag in metadata. Client-side JS library (e.g. Prism.js) handles highlighting to save server compute.

---

## 10. 🚨 Common Pitfalls (Self-Check)

- [x] I separated metadata from blob storage to protect DB performance.
- [x] I addressed the Key Generation collision problem explicitly.
- [x] I included active cleanup for expired pastes to prevent storage leaks.
- [x] I detailed the read path and cache eviction strategy.

---

## 11. 🧮 Scoring Rubric (Self-Evaluation)

| Dimension | 1 (Weak) | 3 (Okay) | 5 (Strong) | Your Score |
|---|---|---|---|---|
| Requirements handling | Vague | Mostly clear | Prioritized + quantified | 5 |
| Architecture clarity | Boxes only | Basic flow | End-to-end + failure-aware | 5 |
| Technical depth | Tool names | Some rationale | Pattern + metric-driven rationale | 5 |
| Trade-off quality | None | Some | Explicit and contextual | 5 |
| Communication | Disorganized | Understandable | Structured + concise | 5 |

---

## 12. ✅ Wrap-up Summary (Final 60-90 Seconds)

1. **Restate key requirements:** We built a highly available, read-heavy Pastebin service supporting configurable expirations and rate limits.
2. **Summarize core architecture:** The core architecture uses API servers fetching pre-generated IDs from a KGS, storing metadata in SQL, and dumping the text blobs into S3.
3. **Call out one intentional trade-off:** We traded the simplicity of storing text in SQL for the operational overhead of S3 + DB separation, protecting our database buffer cache.
4. **Mention one scale-evolution step:** As read traffic surges, we rely heavily on Redis and CDN edge caching to shield the origin servers.
