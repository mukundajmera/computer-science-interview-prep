# Pastebin — Approach & Framework

This guide outlines how to approach the Pastebin system design interview.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. Deconstruct the Problem

Pastebin is fundamentally a **Key-Value Store** problem mixed with a **URL Shortener**. The key differences from a URL shortener are:
1. **Payload Size:** Pastes are much larger (KBs to MBs) than short URLs (~100 bytes).
2. **Data Lifecycle:** Pastes frequently expire or are explicitly deleted.

Your approach should focus on **storage efficiency**, **fast reads**, and **preventing abuse (spam/bots)**.

## 2. Structure the Conversation

1. **Clarify Scope:** Confirm text-only (no images), anonymous creation vs accounts, and expected limits on paste sizes (e.g., 10MB max).
2. **Estimate Scale:** Do back-of-the-envelope math for storage. High read-to-write ratio (10:1 or 100:1) points heavily towards caching.
3. **Define APIs:** Simple `POST /pastes` and `GET /{id}`.
4. **Data Model:** Explain why separating metadata (SQL/NoSQL) and payload (Object Storage) is crucial.
5. **High-Level Design:** Draw the core flow: Client -> LB -> App -> DB/S3/Cache.
6. **Deep Dives:** KGS (Key Generation Service), Expiration cleanup, and Rate Limiting.

## 3. Key Design Decisions

### A. Storage Architecture
- **Naive approach:** Store everything in MySQL (`ID`, `TextBlob`, `Expiration`).
  - *Problem:* DB buffer cache gets polluted with text data, making metadata lookups slow.
- **Optimal approach:** Metadata in DB, Blob in S3/Object Storage.
  - *Why:* S3 is cheap, horizontally scalable for large objects, and keeps the DB highly performant for quick index lookups.

### B. ID Generation
- **Hash Truncation:** `MD5(Paste)` -> take first 7 chars.
  - *Problem:* Collisions require retries.
- **Key Generation Service (KGS):**
  - *Why:* Pre-generates Base62 IDs, puts them in a DB pool, workers fetch batches. Guaranteed O(1) assignment.

### C. Expiration and Cleanup
- **Passive cleanup:** When a user requests an expired paste, delete it.
  - *Problem:* Orphaned pastes (never requested again) waste storage forever.
- **Active cleanup:** A background cron job / sweeper that deletes rows `WHERE expires_at < NOW()`.

## 4. Driving the Deep Dives

When the interviewer asks you to go deep, choose one of these areas where you can show technical maturity:

1. **Handling viral traffic:** Discuss edge caching (CDN) vs application caching (Redis). How to handle cache stampedes.
2. **Abuse prevention:** Token bucket rate limiting per IP.
3. **Client-side Encryption:** If privacy is a concern, the server only sees ciphertext.

## 5. Reviewing Trade-Offs

Always be explicit about what you gave up:
- "I chose to use S3 for text blobs, which adds operational complexity compared to just using a single Postgres DB, but it drastically reduces cost and protects our database performance at scale."
- "I chose a KGS for ID generation. It adds a single point of failure (if not properly clustered) and state to manage, but it completely eliminates write-time collision handling."
