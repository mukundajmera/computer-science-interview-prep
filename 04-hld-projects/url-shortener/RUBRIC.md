# URL Shortener — Interview Scoring Rubric

A structured rubric for evaluating URL Shortener system design interviews across 7 dimensions, each scored from 1 (Poor) to 5 (Strong).

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements Gathering | 10% | Clarifying questions, scope definition |
| 2 | Back-of-Envelope Estimation | 10% | Traffic, storage, bandwidth math |
| 3 | API Design | 15% | RESTful endpoints, error handling, versioning |
| 4 | Data Model | 15% | Schema, indexing, relationships |
| 5 | Architecture | 20% | Components, data flow, high-level diagram |
| 6 | Deep Dives | 20% | Unique ID generation, caching, sharding, hot keys |
| 7 | Trade-offs & Communication | 10% | Pros/cons, justification, clear explanation |

---

## 1. Requirements Gathering

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Jumps straight into design without asking any questions. Misses the read-heavy nature of the system. Does not distinguish functional from non-functional requirements. |
| **3 — Acceptable** | Asks about traffic volume, read/write ratio, and whether custom aliases are needed. Identifies core functional requirements (shorten, redirect) and mentions availability or latency targets. |
| **5 — Strong** | Systematically clarifies scope: DAU, read/write ratio (100:1), URL retention period, custom alias support, analytics depth, and geographic distribution. Explicitly lists what is out of scope (e.g., spam detection, payment). Separates functional and non-functional requirements with specific numbers. |

---

## 2. Back-of-Envelope Estimation

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Provides no numbers or wildly inaccurate estimates. Cannot estimate writes/second from monthly figures. Skips storage and bandwidth entirely. |
| **3 — Acceptable** | Calculates writes/second (~40) and reads/second (~4,000) from the monthly figures. Provides a rough storage estimate (order-of-magnitude correct). Mentions caching memory needs. |
| **5 — Strong** | Derives all key figures methodically: 40 writes/s, 4,000 reads/s, peak at 3× average. Computes per-record size (~160 bytes), total storage over 5 years (~1 TB + indexes ≈ 3–5 TB). Estimates cache size for hot URLs (10M entries ≈ 1.6 GB). Calculates bandwidth (read: ~2 MB/s, write: ~8 KB/s). Notes that 62⁷ = 3.5 trillion codes far exceeds the 6B needed. |

---

## 3. API Design

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Vague or missing API definition. No mention of HTTP methods, status codes, or error handling. Mixes redirect endpoint with management endpoints. |
| **3 — Acceptable** | Defines `POST /api/v1/urls` for creation and `GET /{shortCode}` for redirect. Mentions 301 redirect response and 404 for missing URLs. Includes a stats endpoint. |
| **5 — Strong** | Provides versioned REST endpoints with complete request/response payloads. Covers creation (201), redirect (301/302 with justification), stats (200), and delete (204). Lists error codes (400, 404, 409, 410, 429) with clear semantics. Discusses idempotency (same long URL returns existing short URL) and mentions rate-limiting headers. |

---

## 4. Data Model

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No schema defined or only describes fields informally. Does not mention primary keys or indexes. No discussion of database choice. |
| **3 — Acceptable** | Defines a URL table with `short_code` as primary key, `long_url`, timestamps, and click count. Chooses a database type (SQL or NoSQL) with brief rationale. Mentions at least one secondary index (e.g., `user_id`). |
| **5 — Strong** | Presents a complete schema with URL, click-event, user, and key-pool tables. Justifies NoSQL (simple key-value lookups, horizontal scaling, no joins) over SQL. Defines partition key (`short_code`), GSIs (`user_id`, optionally `long_url` for dedup). Describes the Redis cache structure (key → value, TTL). Explains sharding strategy (hash-based on `short_code`) and replication factor. |

---

## 5. Architecture

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Draws a single box or lists components without showing data flow. Misses critical layers (cache, load balancer). No distinction between read and write paths. |
| **3 — Acceptable** | Shows a layered diagram: clients → load balancer → API servers → cache → database. Describes the read path (cache-first, then DB) and write path (generate key, store, cache). Mentions CDN or analytics at a high level. |
| **5 — Strong** | Draws a complete architecture: CDN/DNS → load balancer with rate limiting → stateless API servers → Redis cache cluster → sharded NoSQL database → analytics pipeline (Kafka → aggregator → analytics DB). Separates read and write flows with clear sequence descriptions. Includes a Key Generation Service as a dedicated component. Discusses edge caching for redirects and async click tracking. |

---

## 6. Deep Dives

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Cannot explain how unique short codes are generated. No mention of caching, sharding, or hot-key handling. Treats the system as a trivial CRUD app. |
| **3 — Acceptable** | Describes at least one ID generation approach (e.g., hash + collision check or counter + base62). Mentions Redis caching with LRU eviction and a TTL. Aware of the hot-key problem for viral URLs but offers only surface-level mitigation (e.g., "use CDN"). |
| **5 — Strong** | Compares multiple ID strategies (counter-based, hash-based, pre-generated KGS) with trade-offs and picks one with justification. Details cache-aside pattern: read-through on miss, write-behind on create, LRU eviction, 24h TTL. Explains hash-based sharding (`hash(short_code) % N`), replication (3 replicas, quorum writes, eventual-consistency reads). Addresses hot keys with layered mitigation: CDN edge caching → replicated Redis keys → local in-memory cache on API servers. Discusses URL expiration (lazy deletion on read + background cleanup). |

---

## 7. Trade-offs & Communication

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Makes design choices without explaining why. Cannot articulate alternatives or downsides. Answers are disorganized and hard to follow. |
| **3 — Acceptable** | Explains at least two trade-offs (e.g., 301 vs 302, SQL vs NoSQL). Communicates the design in a logical order. Responds to interviewer follow-ups adequately. |
| **5 — Strong** | Proactively surfaces trade-offs at each decision point: availability vs consistency (chose AP), latency vs cost (Redis + CDN), 301 vs 302 (configurable), pre-generated keys vs on-demand (chose KGS for speed). Articulates the evolution path (v1 single-server → v2 cached + replicated → v3 multi-region sharded). Communicates clearly, uses diagrams, and structures the answer with time awareness. Wraps up by summarizing key decisions and open questions. |

---

## Quick Calibration Guide

| Total Score (out of 35) | Rating | Recommendation |
|--------------------------|--------|----------------|
| 30–35 | 🟢 Strong Hire | Exceeds expectations across all dimensions |
| 22–29 | 🟡 Hire | Solid fundamentals, minor gaps in depth |
| 15–21 | 🟠 Lean No Hire | Acceptable basics but missing key deep dives |
| 7–14 | 🔴 No Hire | Significant gaps in design thinking |

---

*Use this rubric alongside the [STRONG-ANSWER](./STRONG-ANSWER.md) for calibration and [PITFALLS](./PITFALLS.md) to identify common failure modes.*
