# Pastebin — Interview Scoring Rubric

Use this rubric to evaluate a candidate's (or your own) performance on the Pastebin design interview.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|---|---|---|
| **Requirements & Scale** | 15% | Correctly identifies read-heavy nature. Estimates storage impact of large text blocks and calculates key space requirements. |
| **API & Data Model** | 20% | Separates metadata from payload. Explicitly handles expiration fields and custom aliases in the schema. |
| **Architecture (Read/Write)** | 25% | Clear flow incorporating CDN/Cache, API, Metadata DB, and Object Storage. Handles the ID generation cleanly. |
| **Deep Dives (KGS, Cleanup)** | 25% | Articulates KGS vs Hash collision trade-offs. Designs an active background sweeper for TTL cleanup. |
| **Trade-offs & Constraints** | 15% | Communicates pros/cons of S3 vs DB blob storage, passive vs active cleanup, and caching strategies. |

---

## Performance Bands

### 🟢 Strong Hire (Score: 4.5 - 5.0)
- **Architecture:** Flawlessly separates metadata and text blob storage.
- **Deep Dives:** Recommends a KGS for collision-free ID generation. Understands the necessity of hybrid (active + passive) TTL cleanup to prevent storage leaks.
- **Edge Cases:** Proactively addresses hot-keys/viral pastes using CDN/Redis and discusses rate limiting for abuse prevention.
- **Communication:** Drives the interview, explicitly stating trade-offs before the interviewer asks.

### 🟡 Hire (Score: 3.5 - 4.4)
- **Architecture:** Basic design works. May initially put text in the DB but moves it to S3 when prompted about buffer cache pollution.
- **Deep Dives:** Understands Base62 encoding. Might suggest Hash Truncation but can design collision retry logic.
- **Edge Cases:** Mentions caching but might lack depth on eviction policies or cache stampedes.

### 🟠 Lean No Hire (Score: 2.5 - 3.4)
- **Architecture:** Keeps text and metadata tightly coupled in a relational DB, leading to scaling bottlenecks.
- **Deep Dives:** Fails to recognize the storage leak issue with purely passive TTL cleanup.
- **Edge Cases:** Cannot explain how to mitigate a viral paste causing database overload.

### 🔴 No Hire (Score: < 2.5)
- **Architecture:** Fundamentally broken read/write paths.
- **Deep Dives:** Missing ID generation strategy entirely or uses predictable auto-increment IDs without encoding.
- **Communication:** Disorganized, misses core functional requirements (like expiration).

---

## Specific Signal Checks

- Did they mention a **Key Generation Service (KGS)**? (Strong signal)
- Did they put **Text Blobs in Object Storage (S3)**? (Strong signal)
- Did they implement a **Background TTL Sweeper**? (Strong signal)
