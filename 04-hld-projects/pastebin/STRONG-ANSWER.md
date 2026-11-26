# Pastebin — Model Answer (Time-Boxed)


Say: "I will optimize the pastebin for fast read access and separate text payload storage from metadata to protect database performance."
A strong-answer outline for a 40-minute Pastebin system design interview. Each section includes target timing and key points.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## ⏱️ Time Allocation

| Phase | Duration | Focus |
|-------|----------|-------|
| 1. Requirements & Clarification | 5 min | Scope the problem |
| 2. Estimation | 5 min | Quantify scale |
| 3. API + Data Model + High-Level Design | 10 min | Core architecture |
| 4. Deep Dives | 15 min | Key technical challenges |
| 5. Trade-offs & Wrap-up | 5 min | Justify decisions, summarize |

---

## Phase 1 — Requirements & Clarification (5 min)

"I want to clarify the scope. We are building a system to upload text and generate short, shareable URLs. Are we supporting images or binary files? No, just text. Do users need accounts? No, anonymous usage is fine. Do pastes expire? Yes, configurable expirations."

**State NFRs:** "Given the shareable nature, this will be highly read-heavy, maybe 10:1 or 100:1 reads to writes. We need high availability (99.99%) and low latency for reads."

---

## Phase 2 — Estimation (5 min)

"Let's estimate storage to drive our database choices."
- "Assume 10 million new pastes per month."
- "If average paste is 1KB, that's 10GB/month of text, plus maybe 2-3GB of metadata."
- "Over 3 years, that's ~400-500GB."
- "While 500GB fits on a single disk, the issue is that storing 1KB text blocks inside a relational database will rapidly blow out the buffer cache, leading to disk seeks for every lookup. Therefore, I will separate metadata from the text payloads."

---

## Phase 3 — API + Data Model + High-Level Design (10 min)

### API Endpoints
- `POST /api/v1/pastes` (body: text, expiration. returns: short_url)
- `GET /api/v1/pastes/{shortCode}` (returns: text)

### Data Model
"I'll use a SQL Database (Postgres) for metadata because we want unique constraints on custom aliases, and the data volume (few GBs) easily fits in one instance."
- **Metadata DB:** `short_key`, `s3_path`, `expires_at`, `created_at`.
- **Blob Storage:** S3 for the actual text files.

### Architecture Flow
"A user POSTs text. It hits our API Gateway which enforces rate limits. The App server gets a unique short ID from our Key Generation Service, streams the text to S3 under `s3://bucket/key.txt`, and saves the metadata row in Postgres. For reads, the user hits the short URL, the CDN intercepts. On cache miss, we hit the App Server, which checks Redis, then DB+S3, caching the result on the way back."

---

## Phase 4 — Deep Dives (15 min)

### Deep Dive A: Key Generation Service (KGS)
"How do we generate the 7-character Base62 string? We could hash the text and truncate it, but that causes collisions requiring DB retries. Instead, I'll build a KGS. A background worker generates random 7-character strings, ensures they don't exist, and stores them in a `keys_pool` table. Our API servers request batches of 1,000 keys at a time and keep them in memory. When a paste comes in, assignment is a guaranteed O(1) in-memory operation."

### Deep Dive B: Handling Expirations (Active vs Passive Cleanup)
"Since expired pastes waste S3 and DB space, we need robust cleanup."
- "Passive cleanup: If a user requests a paste and `NOW() > expires_at`, we return 404 and asynchronously delete the S3 object and DB row."
- "Active cleanup: Passive isn't enough because unvisited pastes stay forever. I'll add a cron job / sweeper that runs hourly, querying `SELECT * FROM pastes WHERE expires_at < NOW() LIMIT 1000`. It queues these for a worker to hard-delete from S3 and the DB."

---

## Phase 5 — Trade-offs & Wrap-up (5 min)

"To summarize, we designed a read-optimized Pastebin.
- **Trade-off 1:** We traded the simplicity of storing everything in Postgres for the complexity of S3 + DB. This protects our database performance.
- **Trade-off 2:** We introduced a KGS, adding a single point of failure, but completely eliminated write-time collision handling.
- **Evolution:** As traffic grows, we would lean heavily on CDN edge caching for viral pastes and shard the Postgres DB based on a hash of the `short_key`."
