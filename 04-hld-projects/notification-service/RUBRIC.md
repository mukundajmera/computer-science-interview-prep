# Notification Service — Interview Scoring Rubric

A structured rubric for evaluating Notification Service system design interviews across 7 dimensions, each scored from 1 (Poor) to 5 (Strong).

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## Scoring Overview

| # | Dimension | Weight | Key Signal |
|---|-----------|--------|------------|
| 1 | Requirements Gathering | 10% | Clarifying questions, scope definition |
| 2 | Back-of-Envelope Estimation | 10% | Traffic, storage, queue throughput math |
| 3 | API Design | 15% | RESTful endpoints, priority semantics, idempotency |
| 4 | Data Model | 15% | Schema, notification lifecycle, user preferences |
| 5 | Architecture | 20% | Components, multi-channel routing, data flow |
| 6 | Deep Dives | 20% | Fan-out strategy, delivery guarantees, priority handling, rate limiting per provider |
| 7 | Trade-offs & Communication | 10% | Pros/cons, justification, clear explanation |

---

## 1. Requirements Gathering

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Jumps straight into design without asking any questions. Treats the system as a single-channel push service. Does not distinguish functional from non-functional requirements. |
| **3 — Acceptable** | Asks about traffic volume, supported channels (email/SMS/push), and priority levels. Identifies core functional requirements (send, track, preferences) and mentions latency or throughput targets. |
| **5 — Strong** | Systematically clarifies scope: 100M notifications/day, 500M registered users, supported channels (email, SMS, push, in-app), priority tiers (critical/high/normal/low), delivery guarantee (at-least-once), retry policy, and user opt-out requirements. Explicitly lists what is out of scope (e.g., notification content creation, billing, marketing analytics). Separates functional and non-functional requirements with specific numbers. |

---

## 2. Back-of-Envelope Estimation

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Provides no numbers or wildly inaccurate estimates. Cannot derive messages/sec from daily figures. Skips queue sizing and provider capacity entirely. |
| **3 — Acceptable** | Calculates average throughput (~1,150 notifications/sec) from 100M/day. Provides a rough storage estimate for notification records. Mentions that provider APIs have rate limits. |
| **5 — Strong** | Derives all key figures methodically: 100M/day → ~1,150/sec avg, peak at 3–5× (~5,000/sec). Breaks down by channel (email 60%, push 30%, SMS 10%). Computes notification record size (~500 bytes) and 1-year storage (~18 TB). Estimates queue depth under peak load (~300K messages if consumer lag hits 60 sec). Sizes provider throughput: email providers handle ~1,000/sec per connection, SMS gateways ~200/sec, push providers ~10K/sec batch. Notes that 500M user preference records at ~200 bytes ≈ 100 GB. |

---

## 3. API Design

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Vague or missing API definition. No mention of priority, idempotency, or channel selection. Mixes internal and external APIs. |
| **3 — Acceptable** | Defines `POST /api/v1/notifications` for sending and `GET /api/v1/notifications/{id}/status` for tracking. Mentions priority as a parameter. Includes a preferences endpoint. |
| **5 — Strong** | Provides versioned REST endpoints with complete request/response payloads. Covers single send (201), bulk send (202 Accepted with job ID), status tracking (200), preference management (GET/PUT). Lists error codes (400, 404, 409, 429) with clear semantics. Discusses idempotency keys to prevent duplicate sends. Separates public API (for callers) from internal API (worker-to-provider). Mentions webhook callbacks for delivery status updates. |

---

## 4. Data Model

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | No schema defined or only describes fields informally. Does not mention notification state machine or user preferences. No discussion of database choice. |
| **3 — Acceptable** | Defines a notification table with `id`, `user_id`, `channel`, `status`, `priority`, and timestamps. Mentions a user preferences table. Chooses a database type with brief rationale. |
| **5 — Strong** | Presents a complete schema with notification, notification_log, user_preference, and template tables. Models the notification lifecycle as a state machine (PENDING → QUEUED → SENT → DELIVERED → FAILED). Justifies database choices: relational DB for preferences (complex queries, strong consistency), NoSQL for notification logs (high write throughput, time-series access). Defines partition keys, indexes on `user_id + created_at`, and TTL for log retention. Describes the template storage schema with variable placeholders. |

---

## 5. Architecture

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Draws a single box or lists components without showing data flow. Misses critical layers (message queue, provider adapters). No distinction between channels. |
| **3 — Acceptable** | Shows a layered diagram: API servers → message queue → workers → providers. Describes the routing of notifications to different channels. Mentions a preference service. |
| **5 — Strong** | Draws a complete architecture: API Gateway → Validation Service → Priority Router → per-priority Kafka topics → Channel Workers (email/SMS/push) → Provider Adapters → External Providers. Includes a Preference Service that filters by user opt-outs before queuing. Shows a Template Service for rendering. Includes a DLQ for failed deliveries. Separates the ingestion path from the delivery path. Shows status callback flow from providers back to the notification status store. Discusses rate limiters per provider at the adapter layer. |

---

## 6. Deep Dives

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Cannot explain how notifications are routed to channels. No mention of delivery guarantees, priority queues, or rate limiting. Treats the system as a simple API-to-email call. |
| **3 — Acceptable** | Describes at least one fan-out approach (e.g., topic-per-channel). Mentions at-least-once delivery with retries. Aware of priority levels but offers only surface-level handling (e.g., "process high priority first"). |
| **5 — Strong** | **Fan-out strategy:** Compares topic-per-channel vs topic-per-priority with trade-offs; recommends priority-partitioned topics with dedicated consumer groups so critical alerts are never blocked by bulk emails. **Delivery guarantees:** Explains at-least-once via consumer offset commit after provider ACK; deduplication at the consumer using idempotency keys to achieve effectively-once. **Priority handling:** Separate queues per priority tier with weighted consumer allocation (e.g., 60% capacity for critical, 30% high, 10% normal); starvation prevention with minimum throughput guarantees per tier. **Rate limiting per provider:** Token bucket per provider API (e.g., SendGrid 1,000/sec, Twilio 200/sec); backpressure mechanism pauses consumer when tokens are exhausted; provider failover to secondary providers when primary is throttled. |

---

## 7. Trade-offs & Communication

| Score | Descriptor |
|-------|------------|
| **1 — Poor** | Makes design choices without explaining why. Cannot articulate alternatives or downsides. Answers are disorganized and hard to follow. |
| **3 — Acceptable** | Explains at least two trade-offs (e.g., at-least-once vs exactly-once, push vs pull workers). Communicates the design in a logical order. Responds to interviewer follow-ups adequately. |
| **5 — Strong** | Proactively surfaces trade-offs at each decision point: at-least-once vs exactly-once (chose at-least-once with dedup for simplicity), separate queues per priority vs single queue (chose separate for isolation), single provider vs multi-provider (chose multi for resilience), synchronous vs async delivery (chose async for throughput). Articulates the evolution path (v1 single-channel → v2 multi-channel with queues → v3 priority-aware with provider failover). Communicates clearly, uses diagrams, and structures the answer with time awareness. Wraps up by summarizing key decisions and open questions. |

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
