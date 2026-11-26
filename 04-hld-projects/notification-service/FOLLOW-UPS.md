# Notification Service — Follow-Up Questions

Common follow-up variants an interviewer may ask after the core Notification Service design, along with brief approach outlines for each.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [COMPARISON](./COMPARISON.md)

---

## 1. "How would you handle a bulk campaign to 10M users?"

### Why They Ask

Tests whether your architecture can absorb a massive fan-out without starving real-time transactional notifications or overwhelming downstream providers.

### Approach

- **Ingest as a batch job:** Accept the campaign via a `POST /api/v1/campaigns` endpoint that returns `202 Accepted` with a `job_id`. The campaign specifies a template, audience segment, and scheduling window.
- **Progressive fan-out:** A Campaign Service reads the audience in paginated batches (e.g., 10K users per page), resolves each user's preferences and contact details, renders the template, and publishes individual notification messages to the **low-priority** queue.
- **Throttled emission:** Rate-limit the fan-out to ~500 messages/sec to prevent the campaign from consuming all queue capacity. This delivers 10M notifications in ~5.5 hours — acceptable for marketing.
- **Progress tracking:** The Campaign Service updates a progress counter in Redis (`campaign:{job_id}:sent`). The caller polls a `GET /api/v1/campaigns/{job_id}/status` endpoint for completion percentage and failure count.
- **Isolation:** Because campaigns use the low-priority queue, transactional notifications (OTP, order confirmations) on higher-priority queues are unaffected.

```
Campaign API → Campaign Service (batch reader)
    → User Segment DB (paginated reads, 10K/page)
    → Preference check → Template render
    → Low-priority Kafka topic (throttled 500/sec)
    → Channel workers → Providers
```

**Key trade-off:** Delivery speed vs system stability. Throttling the fan-out ensures campaigns don't degrade real-time notifications, at the cost of hours-long delivery for large audiences.

---

## 2. "How would you add A/B testing for notifications?"

### Why They Ask

Probes your ability to layer experimentation infrastructure on top of the delivery pipeline without complicating the core path.

### Approach

- **Experiment definition:** An Experiment Service stores experiments with variants (e.g., variant A: subject line "Your order shipped!", variant B: "Great news — it's on the way!"). Each experiment specifies a traffic split (50/50), target audience, and success metric (open rate, click-through rate).
- **Assignment at render time:** When a notification enters the channel worker, the worker calls the Experiment Service to get the user's variant assignment. Assignment is deterministic (hash of `user_id + experiment_id`) so the same user always sees the same variant.
- **Template variant selection:** The Template Service stores multiple variants per template. The worker renders the assigned variant.
- **Event tracking:** Track `opened`, `clicked`, and `converted` events per variant. Email opens via a tracking pixel; push opens via the app reporting back; SMS clicks via short-link redirects.
- **Analysis:** Aggregate events in an analytics pipeline. After reaching statistical significance (e.g., 10K observations per variant), the Experiment Service auto-promotes the winning variant.

**Key trade-off:** Experiment granularity vs system complexity. Per-notification experiments give fine-grained data but require variant assignment on every send. A simpler alternative is per-campaign experiments where the entire audience is split once upfront.

---

## 3. "How would you implement smart delivery timing?"

### Why They Ask

Tests whether you can optimize for user engagement by delivering notifications at the best time for each user, rather than firing immediately.

### Approach

- **User activity model:** Track per-user engagement signals (app opens, email opens, push taps) and build a profile of each user's most-active hours. Store as a lightweight histogram (24 hourly slots) per user, per channel.
- **Scheduling decision:** When a non-urgent notification is created (priority: normal or low), the Notification Service checks the user's optimal window. If the current time is outside the window, the notification is scheduled for the next optimal slot.
- **Delayed queue:** Use a scheduled/delayed message mechanism. Options:
  - Kafka: publish with a future timestamp; a scheduler consumer polls and re-publishes when the time arrives.
  - SQS: use `DelaySeconds` (up to 15 min) combined with a scheduler for longer delays.
  - Dedicated scheduler service (e.g., based on a time-sorted data structure or a database with `scheduled_at` index) that promotes messages to the delivery queue at the right time.
- **Timezone handling:** Store the user's timezone in the Preference Service. All scheduling math is done in the user's local time.
- **Override for critical:** Critical and high-priority notifications bypass smart timing and are delivered immediately — a security alert should never be delayed.

**Key trade-off:** Engagement improvement vs delivery latency. Smart timing can increase open rates by 15–30% for marketing notifications, but adds complexity (scheduler service, per-user models) and delays delivery by hours in the worst case. Not appropriate for transactional notifications.

---

## 4. "How would you add real-time in-app notifications?"

### Why They Ask

Tests whether you can extend the system beyond push-based external channels to support a persistent, real-time in-app notification feed.

### Approach

- **New channel: in-app.** Add `in_app` as a channel type alongside email, SMS, and push. In-app notifications are stored rather than sent to an external provider.
- **Storage:** Write in-app notifications to a per-user notification inbox (e.g., Cassandra or DynamoDB, partitioned by `user_id`, sorted by `created_at` descending). Retain the last 100 notifications per user.
- **Real-time delivery via WebSocket:** When the user has the app/website open, maintain a WebSocket connection to a Notification Gateway. When an in-app notification is created, the gateway pushes it to the user's active connection in real-time.
  - Connection registry: track which users are connected to which gateway instance (Redis hash: `user_id → gateway_instance_id`).
  - If the user is offline, the notification is stored and delivered as a batch when the user next opens the app (pull on load).
- **Unread count:** Maintain a counter (`unread_count`) per user in Redis. Increment on new notification, reset on "mark all read." The app polls or receives this via the WebSocket.
- **Read receipts:** `PUT /api/v1/notifications/{id}/read` marks a notification as read and decrements the counter.

```
Notification Worker (in_app channel)
    → Write to Notification Inbox DB
    → Publish to Redis Pub/Sub (user_id channel)
    → Gateway receives, pushes via WebSocket to client

Client opens app → GET /api/v1/notifications?unread=true
    → Read from Inbox DB → Return list
```

**Key trade-off:** WebSocket connections are stateful and resource-intensive. At 500M users, even 1% concurrently online = 5M persistent connections requiring significant gateway infrastructure. A hybrid approach (WebSocket for active users + pull on app open for others) balances real-time experience with resource cost.

---

## 5. "How would you prevent notification fatigue?"

### Why They Ask

Tests whether you think about the user experience holistically — too many notifications cause users to disable them entirely, which is worse than under-notifying.

### Approach

- **Global frequency caps:** Limit the total number of non-critical notifications per user per day (e.g., max 5 push notifications/day, max 3 emails/day). Enforce in the Preference Service before queuing.
- **Per-category caps:** Separate limits by category (e.g., max 2 promotional, max 3 social, unlimited transactional). Stored in the user preference record.
- **Intelligent aggregation/batching:** Instead of sending 10 separate "new follower" notifications, aggregate them into a single digest: "You have 10 new followers." A Digest Service buffers low-priority notifications for a window (e.g., 30 min) and emits a single summary.
- **Smart suppression:** If a user hasn't opened the last N notifications (e.g., 5 consecutive push notifications with no tap), automatically downgrade future notifications of that category to a less intrusive channel (push → email digest) or suppress entirely.
- **User controls:** Expose granular preference UI: per-category opt-in/out, frequency selection (instant / daily digest / weekly digest), and quiet hours.
- **Feedback loop:** Track notification engagement metrics (open rate, dismiss rate, disable rate) per category. If a category's disable rate exceeds a threshold (e.g., 5%), alert the product team and consider reducing frequency system-wide.

**Key trade-off:** Notification reach vs user retention. Aggressive frequency caps reduce engagement per-notification but improve long-term retention by preventing users from disabling notifications entirely. The optimal cap depends on the product — a messaging app tolerates higher frequency than an e-commerce app.

---

## 6. "How would you handle cross-channel delivery orchestration?"

### Why They Ask

Tests whether you can implement a multi-step delivery strategy where channels are tried in sequence with escalation logic, rather than blasting all channels simultaneously.

### Approach

- **Delivery policy per notification type:** Define a channel cascade — e.g., for order updates: try push first → if not delivered in 5 min, send email → if not delivered in 1 hour, send SMS.
- **Orchestration service:** A stateful Orchestrator tracks the delivery attempt chain for each notification. After publishing to the first channel, it sets a timer. If the delivery callback (from the provider) doesn't confirm delivery within the timeout, the Orchestrator promotes the notification to the next channel.
- **Timer implementation:** Use a delay queue (SQS with `DelaySeconds`, Kafka with a scheduled consumer, or a Redis sorted set with score = escalation timestamp). A poller checks for due escalations and triggers the next channel.
- **Stop on success:** If any channel confirms delivery (e.g., push delivered ACK from APNS), cancel the remaining escalation chain. The Orchestrator marks the notification as `DELIVERED` and removes pending timers.
- **Fallback limit:** Cap the cascade at 2–3 channels to avoid spamming the user across every possible medium.

```
Orchestrator → Push channel → wait 5 min
    → Push delivered? → DONE
    → Not delivered → Email channel → wait 1 hour
        → Email delivered? → DONE
        → Not delivered → SMS channel → DONE (final attempt)
```

**Key trade-off:** Delivery reliability vs user experience. Escalation ensures important notifications are eventually delivered, but sending the same message on push, email, and SMS can feel aggressive. Limit cascading to high-priority notification types (e.g., security alerts, payment confirmations) and respect user channel preferences at each step.

---

## Quick Reference

| # | Follow-Up | Core Challenge | Key Concept |
|---|-----------|---------------|-------------|
| 1 | Bulk campaign to 10M users | Fan-out throttling, queue isolation | Progressive fan-out, priority isolation |
| 2 | A/B testing for notifications | Experiment assignment, variant tracking | Deterministic hashing, tracking pixels |
| 3 | Smart delivery timing | Per-user scheduling, timezone handling | Activity histograms, delayed queues |
| 4 | Real-time in-app notifications | WebSocket at scale, notification inbox | Connection registry, pull + push hybrid |
| 5 | Prevent notification fatigue | Frequency caps, intelligent aggregation | Digest service, smart suppression |
| 6 | Cross-channel delivery orchestration | Escalation logic, timer management | Channel cascade, stop-on-success |

---

*See [STRONG-ANSWER](./STRONG-ANSWER.md) for how to structure the base design, and [PITFALLS](./PITFALLS.md) for mistakes to avoid when handling these extensions.*

---

## Pattern Integration Addendum

### 7. "How would you choose transport/channel strategy under changing realtime requirements?"

#### Why They Ask

Tests whether you can avoid defaulting to a single transport and instead choose based on interaction model, freshness target, and connection cost.

#### Approach

- **Channel matrix:** Polling for low-frequency updates, long polling for compatibility fallback, SSE for one-way server push, WebSocket for bidirectional high-frequency flows.
- **Fallback policy:** Keep a deterministic downgrade path (`websocket -> sse -> long polling`) for restrictive networks.
- **Ordering + replay:** Assign monotonic event IDs and replay missed ranges after reconnect.
- **Connection management:** Maintain user-to-connection mapping with heartbeat and idle timeouts.

#### Key trade-off

A richer realtime channel improves UX but increases stateful infrastructure complexity and connection operating cost.

### 8. "How would you escalate contention strategy as load and conflict rates increase?"

#### Why They Ask

Probes whether you can pick the least-complex coordination model first, then escalate only when measured conflict pressure justifies it.

#### Approach

- **Start optimistic:** Version-check + bounded retry for low conflict workloads.
- **Escalate selectively:** Move hot keys to pessimistic lock or serialized queue lanes.
- **Distributed coordination:** Use distributed lock only when cross-node exclusivity is truly required.
- **Safety controls:** Add idempotency keys, retry jitter, lock timeout, and deadlock avoidance rules.

#### Key trade-off

Stronger coordination raises correctness confidence but can reduce throughput and availability under peak contention.

### 9. "How would you make multi-step flows durable and retry-safe?"

#### Why They Ask

Tests your ability to keep business consistency across partial failures in workflows that span services and time.

#### Approach

- **State machine first:** Define explicit lifecycle states and transition guards.
- **Saga style:** Commit each step independently with compensating actions for rollback.
- **Durability:** Persist workflow checkpoints before advancing to the next step.
- **Idempotency:** Require stable idempotency keys for all side-effecting steps.
- **Versioning:** Keep old workflow definitions alive for in-flight instances during upgrades.

#### Key trade-off

Durable orchestration improves resilience and observability but adds runtime overhead and operational complexity.

