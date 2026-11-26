# Notification Service — Common Interview Pitfalls

The top 7 mistakes candidates make in a Notification Service system design interview, why each is a problem, and what the interviewer actually expects.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. Ignoring Provider Rate Limits

### ❌ The Mistake

Designing the delivery pipeline as an unbounded firehose that blasts notifications to external providers (SendGrid, Twilio, APNS/FCM) as fast as possible. Assuming providers have infinite capacity, or never mentioning throttling at all.

### 🎯 What the Interviewer Expects

- Acknowledge that every external provider enforces rate limits (e.g., SendGrid ~1,000 emails/sec, Twilio ~200 SMS/sec, APNS/FCM ~10K push/sec batch).
- Implement a token-bucket or leaky-bucket rate limiter per provider, per channel.
- Describe backpressure: when tokens are exhausted, pause the consumer or buffer messages; do not drop them.
- Discuss provider failover: if the primary email provider is throttled, route overflow to a secondary provider (e.g., SendGrid → Amazon SES).
- Mention that rate limits vary by account tier and can change without notice — make them configurable.

### 💡 Tip

Quantify the problem: "At peak we emit 3,000 emails/sec, but SendGrid allows 1,000/sec — we need three connections or two providers." Numbers make the constraint real and the solution obvious.

---

## 2. No Deduplication Strategy

### ❌ The Mistake

Ignoring the possibility that the same notification is sent twice — once due to a producer retry (Kafka producer ACK timeout) and again because a consumer crashes before committing its offset. The user receives duplicate emails or SMS messages.

### 🎯 What the Interviewer Expects

- Explain how at-least-once delivery inherently risks duplicates.
- Introduce an idempotency key (e.g., `notification_id + channel`) stored in a fast dedup store (Redis with a short TTL).
- Before sending to the provider, check the dedup store; if the key exists, skip the send.
- Discuss the TTL trade-off: too short and late retries duplicate; too long and the dedup store grows large. A 24-hour TTL is a practical default.
- Mention that some providers offer their own dedup (e.g., FCM `collapse_key`), but you should not rely solely on external mechanisms.

### 💡 Tip

Frame it as "effectively-once" delivery: at-least-once at the queue level plus idempotent consumers yields the user experience of exactly-once without the complexity of distributed transactions.

---

## 3. Missing Priority Queues

### ❌ The Mistake

Routing all notifications — critical security alerts, high-priority order confirmations, and low-priority marketing digests — through a single FIFO queue. A bulk marketing campaign to 10M users blocks a password-reset OTP for minutes.

### 🎯 What the Interviewer Expects

- Separate queues (Kafka topics or SQS queues) per priority tier: critical, high, normal, low.
- Dedicated consumer groups per tier with weighted resource allocation (e.g., critical consumers get 60% of delivery capacity).
- Starvation prevention: even the lowest-priority queue gets a guaranteed minimum throughput (e.g., 5% of capacity) so it is never fully starved.
- Explain the routing logic: the API server assigns priority based on the notification type (e.g., OTP → critical, order update → high, newsletter → low), and the priority router publishes to the correct topic.

### 💡 Tip

Use a concrete example: "A user resets their password during a Black Friday campaign. Without priority queues, the OTP sits behind 5M marketing emails. With separate queues, the OTP is delivered in < 3 seconds."

---

## 4. Not Handling Partial Failures

### ❌ The Mistake

Treating the delivery pipeline as all-or-nothing: either the notification is sent or it fails completely. Not considering the scenario where a notification to email succeeds but the same notification to push fails, or where a provider returns a transient error (5xx) vs a permanent one (invalid recipient).

### 🎯 What the Interviewer Expects

- Model notification status per channel independently: a single notification request can be `DELIVERED` on email and `FAILED` on push simultaneously.
- Distinguish transient failures (provider timeout, 5xx) from permanent failures (invalid phone number, unregistered device token).
- Implement exponential backoff with jitter for transient failures (retry 3–5 times, delays of 1s → 2s → 4s).
- Route permanently failed messages to a dead-letter queue (DLQ) for investigation rather than retrying forever.
- Expose per-channel status in the status API so callers can see exactly which channels succeeded.

### 💡 Tip

Draw the state machine on the whiteboard: `PENDING → QUEUED → SENDING → DELIVERED | FAILED → DLQ`. It shows the interviewer you think about the full lifecycle, not just the happy path.

---

## 5. Ignoring User Preferences and Opt-Outs

### ❌ The Mistake

Sending notifications without checking whether the user has opted out of a channel, muted a notification category, or set quiet hours. This is not just a poor user experience — it can violate regulations like GDPR, CAN-SPAM, or TCPA.

### 🎯 What the Interviewer Expects

- A dedicated Preference Service that stores per-user, per-channel, per-category opt-in/opt-out settings.
- Preference check happens **before** queuing, not after — to avoid wasting queue capacity on notifications that will be suppressed.
- Support quiet hours (e.g., "no push between 10 PM – 8 AM in the user's timezone") with timezone-aware scheduling.
- Mention legal compliance: SMS requires explicit opt-in (TCPA), email requires an unsubscribe link (CAN-SPAM), and all channels must honor GDPR right-to-object.
- Cache preferences aggressively (Redis, TTL ~5 min) since they are read on every notification but change rarely.

### 💡 Tip

This is a high-signal topic because it shows you think about the user and legal dimensions, not just the infrastructure. A single sentence — "we check preferences before queuing to respect opt-outs and comply with GDPR" — goes a long way.

---

## 6. No Dead-Letter Queue

### ❌ The Mistake

Retrying failed notifications indefinitely until they succeed or silently dropping them after N retries. No mechanism to capture, inspect, or reprocess messages that persistently fail.

### 🎯 What the Interviewer Expects

- After exhausting retries (e.g., 3–5 attempts with exponential backoff), move the message to a dead-letter queue (DLQ).
- The DLQ is a separate Kafka topic or SQS queue with a long retention period (7–14 days).
- Operational tooling: a dashboard that shows DLQ depth, age of oldest message, and failure reason distribution.
- Manual or automated reprocessing: operators can inspect failed messages, fix the root cause (e.g., update an expired provider API key), and replay the DLQ back into the main pipeline.
- Alerting: if DLQ depth exceeds a threshold (e.g., 10K messages), trigger a PagerDuty alert for on-call engineers.

### 💡 Tip

The DLQ is the safety net that separates production-grade systems from toy systems. Mention it proactively — interviewers notice when candidates think about failure modes before being asked.

---

## 7. Overlooking Template Rendering at Scale

### ❌ The Mistake

Assuming notification content is a static string passed by the caller. Not considering that notifications use templates with dynamic variables (user name, order ID, amount), localization, and per-channel formatting (HTML for email, plain text for SMS, structured payload for push).

### 🎯 What the Interviewer Expects

- A Template Service that stores pre-approved templates with variable placeholders (e.g., `Hello {{user_name}}, your order #{{order_id}} has shipped`).
- Rendering happens in the channel workers — after routing, before sending — so the template is formatted for the correct channel.
- Support localization: templates exist in multiple languages; the user's locale (from preferences) determines which variant to render.
- Pre-compile templates (e.g., Handlebars, Jinja2) and cache compiled versions to avoid parsing overhead on every render.
- At 5,000 notifications/sec peak, template rendering adds ~1 ms per notification — manageable, but mention that you would benchmark and keep templates simple.

### 💡 Tip

Mention that separating templates from code enables non-engineering teams (product, marketing) to update notification content without a code deploy. This demonstrates product-awareness beyond pure infrastructure.

---

## Summary Table

| # | Pitfall | What's Missing | Scoring Impact |
|---|---------|---------------|----------------|
| 1 | No provider rate limiting | External API constraint awareness | Deep Dives dimension: -2 to -3 points |
| 2 | No deduplication | Effectively-once delivery logic | Deep Dives dimension: -2 to -3 points |
| 3 | No priority queues | Isolation between notification tiers | Architecture dimension: -2 to -3 points |
| 4 | No partial failure handling | Per-channel status and retry logic | Deep Dives dimension: -2 to -3 points |
| 5 | No user preference checks | Regulatory compliance, user respect | Requirements dimension: -2 to -3 points |
| 6 | No dead-letter queue | Operational maturity, failure recovery | Architecture dimension: -1 to -2 points |
| 7 | No template rendering plan | Content management at scale | Data Model dimension: -1 to -2 points |

---

*See [RUBRIC](./RUBRIC.md) for full scoring criteria and [STRONG-ANSWER](./STRONG-ANSWER.md) for how to address each of these correctly.*

---

## 8. Choosing the Wrong Realtime Transport by Default

### ❌ The Mistake

Using one channel for all realtime scenarios (usually WebSocket) without validating whether communication is one-way, bidirectional, bursty, or mostly idle.

### 🎯 What the Interviewer Expects

- A transport decision matrix tied to product behavior and cost profile.
- Explicit fallback strategy and reconnect replay semantics.
- Ordering scope and deduplication plan for multi-device users.

### 💡 Tip

State channel selection as a requirement-driven decision, not a technology preference.

## 9. Over- or Under-Coordinating Contention Paths

### ❌ The Mistake

Either adding distributed locks too early or ignoring conflicts until oversell/double-assignment incidents appear.

### 🎯 What the Interviewer Expects

- An escalation ladder: optimistic -> pessimistic/serialized -> distributed coordination.
- Measurable triggers (conflict rate, retry depth, lock wait time).
- Idempotent retries, bounded backoff, and failure-mode handling.

### 💡 Tip

Show how you would isolate hot keys rather than globally locking the entire workload.

## 10. Missing Durable Workflow Boundaries for Multi-step Operations

### ❌ The Mistake

Treating multi-service flows as a single best-effort request chain without durable checkpoints, compensation, or idempotency.

### 🎯 What the Interviewer Expects

- Explicit step state machine and compensation strategy.
- Durable checkpointing and resume path after crash/redeploy.
- Idempotency requirements for every side-effecting step.
- Versioning plan for in-flight workflow upgrades.

### 💡 Tip

If a flow can partially succeed, describe how it recovers before describing happy-path latency.

