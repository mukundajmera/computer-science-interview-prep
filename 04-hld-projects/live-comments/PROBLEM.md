
# Live Comments System

## Problem Statement

Design a large-scale live comment stream for broadcasts with low-latency fanout and replay for late joiners.

---

## Requirements and Constraints

### Functional Requirements

1. Post comments on a live stream
2. Broadcast comments to active viewers in near real time
3. Replay recent comments for reconnecting users

### Non-Functional Requirements

| Requirement | Target |
|---|---|
| Comment fanout latency | < 250 ms P99 |
| Availability | 99.99% |
| Scale | Millions of concurrent viewers |
| Consistency | Eventual ordering by stream partition |

### Out of Scope

- Full recommendation/ads internals.
- Back-office analytics tooling.
- Third-party billing and compliance details.

---

## High-Level Design Outline

- API Gateway + stateless app tier
- Domain service layer
- Cache + durable primary store
- Async pipeline for fanout/indexing/notifications
- Monitoring, alerting, and replay controls

### Sample APIs

```http
POST /api/v1/live/{streamId}/comments
GET /api/v1/live/{streamId}/comments?cursor=...
GET /api/v1/live/{streamId}/events/stream
POST /api/v1/live/{streamId}/acks
```

---

## Scoring Rubric

- Requirement framing and boundary definition
- Capacity assumptions tied to architecture
- Correct consistency model on critical operations
- Clear failure handling and degraded mode

See [RUBRIC](./RUBRIC.md).

## Common Pitfalls

See [PITFALLS](./PITFALLS.md).

## Follow-Up Questions

See [FOLLOW-UPS](./FOLLOW-UPS.md).

## Variants and Extensions

- Global multi-region rollout.
- Cost-optimized variant with relaxed freshness.
- Compliance-first variant with stricter audit rules.

## Related Links

- [APPROACH](./APPROACH.md)
- [DESIGN](./DESIGN.md)
- [STRONG-ANSWER](./STRONG-ANSWER.md)
- [03-hld-concepts/real-time-updates](../../03-hld-concepts/real-time-updates/)
- [03-hld-concepts/message-queues](../../03-hld-concepts/message-queues/)
- [03-hld-concepts/read-scaling](../../03-hld-concepts/read-scaling/)
- [solutions/hld-live-comments.md](../../solutions/hld-live-comments.md)
