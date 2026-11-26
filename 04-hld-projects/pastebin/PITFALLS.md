# Pastebin - Common Pitfalls

These are the most frequent mistakes candidates make when designing Pastebin.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. Storing Text Blobs Directly in a SQL Database

**The Trap:** It's tempting to create a table `pastes (id, text_content, created_at)` and store the entire multi-kilobyte text block in the database.

**Why it's a Pitfall:**
Relational databases use memory (Buffer Pool/Cache) to keep frequently accessed pages in RAM. Storing large text blobs pollutes this cache rapidly, causing high cache eviction rates and forcing the DB to perform slow disk I/O for simple metadata queries.

**The Mitigation:**
Separate concerns. Store metadata (keys, dates) in the DB, and store the actual text payloads in Object Storage (like Amazon S3) or a dedicated distributed file system.
*Validation:* "I will use S3 for text storage to ensure our DB buffer pool is optimized for fast metadata lookups."

## 2. Relying Exclusively on Passive Expiration

**The Trap:** Implementing paste expiration by only checking `expires_at < NOW()` when a user attempts to read a paste, and deleting it then.

**Why it's a Pitfall:**
If a paste is created and *never accessed again*, it will sit on disk forever. Given millions of pastes per month, this leads to a massive, silent storage leak.

**The Mitigation:**
Implement a hybrid approach:
1. Passive: Delete on read if expired.
2. Active: A background worker (sweeper) periodically scans the DB for expired records and explicitly deletes them from both the DB and S3 to reclaim space.
*Validation:* Mention cron jobs, message queues, or TTL features native to NoSQL/Redis.

## 3. Ignoring ID Collisions with Hash Truncation

**The Trap:** Generating short links using `MD5(long_url)[:7]`.

**Why it's a Pitfall:**
Truncating an MD5 hash dramatically increases the probability of a hash collision (Pigeonhole Principle/Birthday Paradox). If two different pastes result in the same 7-character string, the DB write will fail (if unique constraint exists) or silently overwrite data.

**The Mitigation:**
Either implement a robust retry loop (detect collision -> append salt -> hash again) or better yet, use a **Key Generation Service (KGS)** that pre-generates guaranteed unique IDs.

## 4. Unbounded Paste Sizes

**The Trap:** Allowing users to submit arbitrarily large text payloads.

**Why it's a Pitfall:**
Malicious users or runaway bots can upload 500MB text files, exhausting network bandwidth, memory on API servers, and storage limits rapidly.

**The Mitigation:**
Enforce strict validation at the API Gateway / Load Balancer level (e.g., max payload size 10MB) and return a `413 Payload Too Large` error.

## 5. Sequential/Predictable Short IDs

**The Trap:** Using an auto-incrementing database ID and simply converting it to Base62 (e.g., ID 1 -> '1', ID 2 -> '2').

**Why it's a Pitfall:**
Security/Privacy risk. An attacker can easily scrape the entire service by incrementing the URL, reading every paste sequentially.

**The Mitigation:**
Shuffle the Base62 alphabet, use a Feistel cipher, or ensure the Key Generation Service generates random strings rather than sequential ones.
