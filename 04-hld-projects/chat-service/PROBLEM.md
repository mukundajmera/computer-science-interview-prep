# Chat/Messaging Service System

## Problem Statement

Design a WhatsApp-like real-time messaging system that supports one-to-one and group chat, reliable delivery across unstable networks, and multi-device synchronization.

> Related docs: [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [case study](../../case-studies/whatsapp-messaging/README.md)

---

## Functional Requirements

1. One-to-one real-time messaging.
2. Group chat (parameterized limits; interviewer variant often uses 100 members, default practice target 256).
3. Message delivery lifecycle (`sent`, `delivered`, `read`).
4. Offline message retrieval on reconnect (target retention up to 30 days).
5. Multi-device sessions per user (mobile/web/desktop).
6. Conversation history with cursor pagination.
7. Presence and last-seen visibility controls.
8. Typing indicators.

---

## Non-Functional Requirements

| Requirement | Target |
|---|---|
| Availability | 99.99% |
| Online delivery latency | < 100ms within region |
| Throughput | 100K+ msg/s, burst-ready |
| Connection scale | 10M+ concurrent sessions |
| Durability | No acknowledged message loss |
| Consistency | Strong for persistence, eventual for presence/read receipts |

---

## Assumptions and Constraints

- DAU around 500M, average 40 sends/user/day.
- Average message payload around 100 bytes (text-focused baseline).
- Users frequently change network quality and reconnect.
- End-to-end encryption implementation details are out of scope, but its architectural implications must be discussed.

---

## Out of Scope

- Voice/video call media plane.
- Full media pipeline implementation.
- Registration/auth onboarding internals.
- Full-text message search.

---

## Core APIs (sample)

```http
POST /api/v1/messages
GET /api/v1/conversations/{id}/messages?cursor=...&limit=50
POST /api/v1/conversations
PATCH /api/v1/messages/{id}/read
```

Realtime channel (WebSocket or equivalent):

```text
client -> server: send_message, ack, typing, heartbeat
server -> client: new_message, delivered, read, presence_update
```

---

## Key Design Challenges

| Challenge | Why It Is Hard |
|---|---|
| Connection management | Millions of long-lived stateful connections |
| Ordering and replay | Distributed writes + reconnect gaps |
| Offline durability | Must drain backlog without duplicates |
| Group fan-out | Large groups amplify writes and delivery tasks |
| Multi-device sync | Independent session cursors and ack behavior |
| Presence correctness | Last-seen and privacy rules under eventual consistency |

---

## Version Roadmap

| Version | Scope |
|---|---|
| v1-basic | 1:1 messaging, basic delivery, simple persistence |
| v2-scaled | Groups, queue-driven delivery, presence and receipts |
| v3-distributed | Multi-region, multi-device sync, advanced ordering/replay |
