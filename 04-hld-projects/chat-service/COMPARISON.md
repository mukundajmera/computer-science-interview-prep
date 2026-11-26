# Chat/Messaging Service — System Comparison

How the Chat/Messaging Service compares to related systems: Notification Service, Email System, and Social Media Feed. Understanding these parallels strengthens your ability to discuss trade-offs and reuse patterns across interviews.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [STRONG-ANSWER](./STRONG-ANSWER.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md)

---

## Chat Service vs Notification Service

A Notification Service delivers transient alerts (push notifications, in-app banners, emails) to users. Chat Service delivers persistent, bidirectional messages in conversations. Both push data to users in real-time, but the data model, persistence guarantees, and interaction patterns differ fundamentally.

| Dimension | Chat Service | Notification Service | Key Difference |
|-----------|-------------|---------------------|----------------|
| **Communication model** | Bidirectional — users send *and* receive messages | Unidirectional — system pushes alerts to users | Chat requires a full-duplex channel (WebSocket); notifications are server-to-client only |
| **Message persistence** | Messages stored permanently; users can scroll back through history | Notifications are transient; often discarded after display or TTL expiry | Chat needs durable storage (Cassandra); notifications may use only a short-lived queue |
| **Connection type** | Persistent WebSocket connections for real-time delivery | Can use push services (APNs/FCM), WebSocket, or polling | Chat *requires* persistent connections; notifications can fire-and-forget via platform push |
| **Conversation context** | Messages belong to conversations with ordering and threading | Notifications are standalone events, no conversation threading | Chat must maintain conversation state and message ordering; notifications are stateless |
| **Delivery guarantee** | At-least-once with ACK; offline messages queued and drained on reconnect | Best-effort or at-least-once; some notifications are acceptable to lose | Chat has stricter durability — every message must eventually be delivered |
| **Fan-out pattern** | 1:1 or group (up to 256 members) | Broadcast to millions (e.g., "new feature available") | Notification fan-out is wider but shallower; chat fan-out is narrower but deeper (conversation context) |
| **User interaction** | Users read, reply, react — messages drive further conversation | Users tap/dismiss — notifications are terminal events | Chat is interactive; notifications are informational |
| **Read receipts** | Yes — sender sees "delivered" and "read" status | Rarely — at most "opened" tracking for analytics | Chat read receipts are a core feature; notification open tracking is optional analytics |

### Shared Patterns

- Both use **persistent connections or push channels** to deliver data to clients in real-time.
- Both need **offline handling** — queueing undelivered items for later delivery.
- Both benefit from **per-user routing** — knowing which server or device a user is connected to.
- Both use **Kafka or similar message queues** for decoupled, reliable delivery pipelines.

---

## Chat Service vs Email System

An Email System (e.g., Gmail, Outlook) uses a store-and-forward model with protocols like SMTP/IMAP. Chat Service uses persistent connections for real-time delivery. Both deliver messages between users, but the latency expectations, protocol stack, and storage patterns diverge significantly.

| Dimension | Chat Service | Email System | Key Difference |
|-----------|-------------|-------------|----------------|
| **Delivery latency** | Real-time (< 100 ms for online users) | Store-and-forward (seconds to minutes is acceptable) | Chat optimizes for instant delivery; email tolerates significant delay |
| **Connection model** | Persistent WebSocket connections; always-on | Clients connect periodically (IMAP IDLE or polling); no persistent app-level connection required | Chat requires maintaining millions of open connections; email clients can be offline for hours |
| **Protocol** | Custom WebSocket events over TCP/TLS | SMTP (send), IMAP/POP3 (receive) — standardized, federated protocols | Email is federated across providers; chat is typically a single-provider walled garden |
| **Message size** | Small (100 bytes avg text, 10 KB max) | Large (up to 25 MB with attachments) | Email needs attachment storage (object store); chat messages fit in a key-value store |
| **Threading model** | Conversations with strict time ordering | Threads with `In-Reply-To` headers; can be messy and non-linear | Chat ordering is absolute (TIMEUUID); email threading is heuristic and often broken |
| **Presence & typing** | Real-time presence (online/offline), typing indicators | No presence concept; no typing indicators | Chat is synchronous-feeling; email is inherently asynchronous |
| **Storage model** | Cassandra (write-optimized, time-series per conversation) | Blob storage for messages + full-text index for search | Email prioritizes search; chat prioritizes fast sequential reads of recent messages |
| **Spam/abuse** | Minimal (users must be contacts or group members) | Major concern — spam filtering is a core service | Email systems invest heavily in spam detection (SpamAssassin, ML filters); chat relies on contacts graph |
| **Federation** | Closed system (WhatsApp, Telegram) | Open federation (any SMTP server can send to any other) | Email's open federation creates spam; chat's closed model simplifies trust but limits interoperability |

### Shared Patterns

- Both are fundamentally **message delivery systems** — accept a message from a sender, route it to a recipient.
- Both need **offline storage** — email in mailboxes, chat in offline message queues.
- Both have **inbox views** — a sorted list of conversations/threads with unread counts.
- Both must handle **multi-device access** — read state and message sync across devices.

---

## Chat Service vs Social Media Feed

A Social Media Feed (e.g., Twitter timeline, Instagram feed) distributes content from creators to followers. Chat delivers messages between participants in private conversations. Both involve fan-out, but the relationship model, content lifecycle, and delivery semantics differ.

| Dimension | Chat Service | Social Media Feed | Key Difference |
|-----------|-------------|------------------|----------------|
| **Relationship model** | Mutual participation — both parties are in the conversation | Asymmetric follow — creator posts, followers consume | Chat is mutual/private; feed is public/asymmetric |
| **Fan-out pattern** | Small fan-out (1:1 or groups up to 256) | Massive fan-out (celebrity with 50M followers) | Feed fan-out is orders of magnitude larger; chat fan-out is bounded by group size |
| **Fan-out strategy** | Fan-out-on-write for all messages (push to each recipient) | Hybrid: fan-out-on-write for normal users, fan-out-on-read for celebrities | Chat can always push; feed must handle extreme fan-out asymmetry |
| **Content ordering** | Strict chronological within each conversation | Algorithmic ranking (relevance, engagement, recency) | Chat order is sacred — users notice misordering; feed ranking is a feature, not a bug |
| **Delivery guarantee** | Every message must be delivered to every participant | Best-effort — missing a post in a feed is tolerable | Chat has zero-tolerance for message loss; feed can trade completeness for performance |
| **Real-time requirement** | Mandatory (< 100 ms for online users) | Nice-to-have (seconds to minutes is acceptable for feed refresh) | Chat is latency-critical; feed prioritizes throughput over latency |
| **Content lifecycle** | Messages are permanent (unless explicitly deleted) | Posts are permanent but feed visibility fades with time/algorithm | Chat history is user-controlled; feed visibility is algorithm-controlled |
| **Privacy model** | Private by default — only conversation participants see messages | Public or semi-public — posts visible to followers/everyone | Chat requires strict access control per conversation; feed access is broader |
| **Storage access pattern** | Per-conversation reads (partition by conversation_id) | Per-user timeline reads (precomputed feed or merge at read time) | Chat reads are narrow (one conversation); feed reads aggregate from many sources |

### Shared Patterns

- Both use **fan-out** as a core mechanism — distributing content from a source to multiple recipients.
- Both use **message queues (Kafka)** for decoupled, async delivery pipelines.
- Both need **caching** for hot data — recent messages in chat, precomputed timelines in feed.
- Both face the **thundering herd problem** — a popular group message or viral post triggers a burst of deliveries.

---

## Cross-Cutting Comparison Summary

| Concern | Chat Service | Notification Service | Email System | Social Media Feed |
|---------|-------------|---------------------|-------------|------------------|
| **Delivery latency** | < 100 ms | < 1 sec | Seconds to minutes | Seconds to minutes |
| **Connection model** | Persistent WebSocket | Push services / WebSocket | IMAP IDLE / polling | HTTP polling / streaming |
| **Message persistence** | Permanent (Cassandra) | Transient (short TTL) | Permanent (blob + index) | Permanent (with ranking decay) |
| **Fan-out size** | 1–256 members | 1–millions | 1–hundreds (CC/BCC) | 1–millions (followers) |
| **Ordering** | Strict chronological (TIMEUUID) | Chronological (best-effort) | Thread-based (heuristic) | Algorithmic ranking |
| **Primary storage** | Cassandra + Redis + PostgreSQL | Redis / DynamoDB | Object store + search index | Cassandra / Redis (precomputed feeds) |
| **Key challenge** | Connection scaling, message ordering | Delivery at broadcast scale | Spam filtering, federation | Fan-out for celebrities, ranking |

---

## When to Reference These Comparisons

- **Notification Service comes up?** Reuse the WebSocket delivery layer and Kafka pipeline from your chat design, but simplify: remove conversation state, threading, and read receipts. Shift focus to broadcast fan-out and platform push integration.
- **Email System comes up?** Highlight that chat is "email made real-time" — same message routing core, but replace store-and-forward with persistent connections. Add presence and typing indicators. Remove SMTP federation and spam filtering.
- **Social Media Feed comes up?** The fan-out pattern is the shared concept. Explain that chat uses fan-out-on-write universally (bounded group sizes), while feed needs hybrid fan-out (fan-out-on-read for celebrities). Chat ordering is strict; feed ordering is ranked.

---

*See [DESIGN](./DESIGN.md) for the full Chat Service architecture and [FOLLOW-UPS](./FOLLOW-UPS.md) for interview extensions that push toward these related systems.*
